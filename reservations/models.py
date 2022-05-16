from django.db import models
from django.utils import timezone

from users.models import Group, SystemUser, PermissionTag


class Term(models.Model):
    """
    공간 예약을 위한 약관
    - Term : Group = N : 1 (한 그룹에 여러 약관이 등록될 수 있으므로)
    - Term : Space = 1 : N (한 약관은 여러 공간에서 사용될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='registered_terms')

    title = models.CharField('제목', max_length=255, null=False)
    body = models.TextField('내용', null=False, blank=True)

    class Meta:
        verbose_name = '약관'
        verbose_name_plural = '약관 목록'


class Space(models.Model):
    """
    예약의 대상이 되는 공간
    - Space : Group = N : 1 (한 그룹에 여러 공간이 등록될 수 있으므로)
    - Space : Term = N : 1 (한 약관이 여러 공간에서 사용될 수 있으므로)
    - Space : PermissionTag = N : 1 (한 권한 태그가 여러 공간에서 요구될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='소속 그룹', related_name='registered_spaces')

    term = models.ForeignKey(Term, null=True, on_delete=models.PROTECT,
                             verbose_name='등록 약관', related_name='using_spaces')

    name = models.CharField('공간 이름', max_length=255)

    # term과의 연결은 유지하되, Term의 내용이 변경되었을 때 선택적으로 내용을
    # Space instance에 반영할 수 있도록 구현
    term_body = models.TextField('약관 본문', null=True, blank=True)

    required_permission = models.ForeignKey(PermissionTag, on_delete=models.PROTECT, null=True,
                                            related_name='requiring_spaces', verbose_name='요구 권한')

    class Meta:
        verbose_name = '공간'
        verbose_name_plural = '공간 목록'


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

    dt_from = models.DateTimeField('예약 시작 일시', blank=False, null=False)
    dt_to = models.DateTimeField('예약 해제 일시', blank=False, null=False)

    class Meta:
        verbose_name = '예약'
        verbose_name_plural = '예약 목록'

    def __str__(self):
        return self.member.username

    @classmethod
    def get_reservation_of_week(cls, target_day: timezone.datetime, space: Space):
        target_weekday = target_day.weekday()
        monday_start = target_day - timezone.timedelta(days=target_weekday)
        sunday_end = monday_start + timezone.timedelta(days=7) - timezone.timedelta(seconds=1)

        in_range_reservations = Reservation.objects.filter(space=space, dt_from__gte=monday_start,
                                                           dt_to__lte=sunday_end)

        reservation_per_weekdays = []
        for i in range(7):
            tmp = {_h: None for _h in range(24)}

            start = monday_start + timezone.timedelta(days=i)
            end = start + timezone.timedelta(days=1)

            h = start
            while h < end:
                for reservation in in_range_reservations.filter(dt_from__gte=h,
                                                                dt_to__lt=h + timezone.timedelta(hours=1)):
                    tmp[h.hour] = reservation
                h += timezone.timedelta(hours=1)
            reservation_per_weekdays.append(tmp)

        return reservation_per_weekdays

    @staticmethod
    def get_datetime(year, month, day):
        if not (year and month and day):
            target_day = timezone.now()
        else:
            try:
                target_day = timezone.datetime(int(year), int(month), int(day))
            except Exception:
                return None

        target_day = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
        return target_day
