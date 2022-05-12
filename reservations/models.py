from django.db import models

from users.models import Group, SystemUser, PermissionTag


class Term(models.Model):
    """
    공간 예약을 위한 약관
    - Term : Group = N : 1 (한 그룹에 여러 약관이 등록될 수 있으므로)
    - Term : Space = 1 : N (한 약관은 여러 공간에서 사용될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)
    modified_at = models.DateTimeField('수정 일시', auto_now=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='registered_terms')
    body = models.TextField('내용', null=False, blank=True)


class Space(models.Model):
    """
    예약의 대상이 되는 공간
    - Space : Group = N : 1 (한 그룹에 여러 공간이 등록될 수 있으므로)
    - Space : Term = N : 1 (한 약관이 여러 공간에서 사용될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='소속 그룹', related_name='registered_spaces')

    term = models.ForeignKey(Term, null=True, on_delete=models.PROTECT,
                             verbose_name='등록 약관', related_name='using_spaces')

    # term과의 연결은 유지하되, Term의 내용이 변경되었을 때 선택적으로 내용을
    # Space instance에 반영할 수 있도록 구현
    term_body = models.TextField('약관 본문', null=True, blank=True)


class Reservation(models.Model):
    """
    예약 내역
    - Reservation : Space = N : 1 (한 공간에 여러 예약 내역이 있을 수 있으므로)
    - Reservation : SystemUser = N : 1 (한 사용자가 여러 건의 예약을 할 수 있으므로)
    - Reservation : PermissionTag : N : M (예약이 여러 개의 권한을 요구할 수도 있고, 권한이 여러 예약에서 요구될 수 있으므로)
    """
    space = models.ForeignKey(Space, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 공간', related_name='reservations_as_space')

    member = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                               verbose_name='예약자', related_name='reservations_as_member')

    promised_term_body = models.TextField('동의 약관 본문', null=True, blank=True)

    required_permissions = models.ManyToManyField(PermissionTag, db_index=True,
                                                  related_name='requiring_reservations', verbose_name='요구 권한')

    dt_from = models.DateTimeField('예약 시작 일시', blank=False, null=False)
    dt_to = models.DateTimeField('예약 해제 일시', blank=False, null=False)
