import string
import random

from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinLengthValidator


class SystemUser(AbstractUser):
    """
    시스템 사용자
    - SystemUser : Group = 1 : 1 (그룹 매니저)
    - SystemUser : MemberInfo = 1 : N (여러 그룹에 소속될 수 있음)
    - SystemUser : JoinRequest = 1 : N (여러 그룹에 가입 요청을 할 수 있음)
    """
    # (Not inherit)
    first_name = None
    last_name = None

    # 그룹에서 중복되지 않는 경우 기본적으로 사용할 닉네임
    nickname = models.CharField('닉네임', max_length=30, blank=False, null=False)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'


class Group(models.Model):
    """
    여러 사용자를 포함하는 그룹
    - Group : SystemUser = 1 : 1 (그룹 매니저)
    - Group : MemberInfo = 1 : N (그룹에 다수의 멤버가 소속될 수 있음)
    - Group : PermissionTag = 1 : N (그룹에 여러 권한 태그가 있을 수 있음)
    - Group : JoinRequest = 1 : N (한 그룹에 여러 그룹 요청이 올 수 있음)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    name = models.CharField('그룹명', max_length=20, blank=False, null=False, unique=True, db_index=True)
    manager = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                                verbose_name='그룹 관리자', related_name='managing_groups')

    is_public = models.BooleanField('그룹 공개 여부', default=False)

    _INVITE_CODE_LENGTH = 5
    _INVITE_CODE_CHARS = string.ascii_letters + string.digits
    invite_code = models.CharField('그룹 초대 코드', default=None, unique=True,
                                   max_length=_INVITE_CODE_LENGTH, validators=[MinLengthValidator(_INVITE_CODE_LENGTH)])

    members = models.ManyToManyField(SystemUser, db_index=True,
                                     related_name='belonged_groups', verbose_name='멤버 목록')

    class Meta:
        verbose_name = '그룹'
        verbose_name_plural = '그룹 목록'

    @classmethod
    def start_new_group(cls, manager: SystemUser, group_name: str, is_public: bool) -> Group:
        """
        새 그룹을 생성해 반환하는 메서드

        :param manager: 그룹 관리자
        :param group_name: 생성할 그룹의 이름(unique)
        :param is_public: 공개 여부
        :return: 새로 생성된 그룹

        :except IntegrityError: 이미 사용중인 그룹명인 경우
        :except Exception: 그룹 개설을 요청한 사용자가 50개 이상의 그룹을 관리하고 있는 경우
        """
        # 1. manager가 이미 50개 그룹의 매니저인 경우 예외를 발생시킴
        if len(manager.managing_groups.all()) >= 50:
            raise Exception('50개 이상의 그룹을 관리할 수 없습니다.')

        # 2. 이미 사용중인 그룹명인 경우 생성 거절됨
        try:
            # 3. Unique한 그룹 초대 코드를 생성
            invite_code = cls.get_unique_invite_code()
            new_group = Group.objects.create(
                manager=manager, name=group_name, is_public=is_public, invite_code=invite_code
            )
        except IntegrityError as e:
            raise e

        # 4. 해당 그룹의 첫 멤버로 그룹 매니저를 등록
        new_group.members.add(manager)

        return new_group

    @classmethod
    def get_unique_invite_code(cls) -> str:
        """
        Unique한 Group.invite_code를 새로 생성해 반환하는 메서드
        생성에 사용할 문자와 invite_code의 길이는 각각 Group._INVITE_CODE_CHARS과 Group._INVITE_CODE_LENGTH에 의해 결정된다.

        :return: Unique한 invite_code
        """
        while True:
            new_invite_code = ''.join(random.sample(cls._INVITE_CODE_CHARS, cls._INVITE_CODE_LENGTH))
            existing_invite_code = cls.objects.values('invite_code')
            if new_invite_code not in existing_invite_code:
                break
        return new_invite_code


class PermissionTag(models.Model):
    """
    그룹 내에서의 권한을 표시하기 위한 태그
    해당 태그의 존재 여부로 그룹 사용자의 특정 기능의 사용 가능 여부가 정해진다.
    - PermissionTag : MemberInfo = N : M (여러 사용자가 여러 권한을 가질 수 있으므로)
    - PermissionTag : Group = N : 1 (권한은 그룹 안에서 유효하므로)
    """
    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='registered_permission_tags')
    body = models.CharField(max_length=10, blank=False, null=False)

    class Meta:
        verbose_name = '권한 태그'
        verbose_name_plural = '권한 태그 목록'


class MemberInfo(models.Model):
    """
    그룹 내에서 사용자를 가리키기 위한 고유 정보
    - MemberInfo : SystemUser = N : 1 (사용자가 여러 그룹에 소속될 수 있으므로)
    - MemberInfo : Group = N : 1 (그룹 내에 여러 사용자가 소속될 수 있으므로)
    - MemberInfo : Block = 1 : N (한 사용자가 여러 번 제한될 수 있으므로)
    - MemberInfo : PermissionTag = 1 : N (한 사용자가 여러개의 권한을 가질 수 있으므로)
    """
    created_at = models.DateTimeField('가입 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='member_infos')
    user = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                             verbose_name='대상 유저', related_name='group_infos')

    # 그룹 내에서 사용할 닉네임 (그룹 내에서 Unique함)
    nickname = models.CharField('닉네임', max_length=30, blank=False, null=False)

    # 그룹 내에서 해당 사용자가 가지는 권한의 목록
    permission_tags = models.ManyToManyField(PermissionTag, db_index=True,
                                             related_name='permissions', verbose_name='권한 목록')

    class Meta:
        verbose_name = '그룹 내 사용자 정보'
        verbose_name_plural = '그룹 내 사용자 정보 목록'

        constraints = (
            # 그룹 내에서 nickname field가 Unique하도록 제한 (raise IntegrityError)
            models.UniqueConstraint(
                fields=['group', 'nickname'],
                name='unique nicknames'
            ),
        )


class Block(models.Model):
    """
    그룹 내 활동 제한 내역
    - Block : MemberInfo = N : 1 (한 사용자가 여러 번 제한될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    member_info = models.ForeignKey(MemberInfo, null=False, on_delete=models.CASCADE,
                                    verbose_name='대상 멤버 정보', related_name='blocks')
    dt_from = models.DateTimeField('제한 시작 일시', blank=False, null=False)
    dt_to = models.DateTimeField('제한 해제 일시', blank=False, null=False)

    class Meta:
        verbose_name = '제한 내역'
        verbose_name_plural = '제한 내역'

        # constraints = (
        #     # dt_from이 반드시 dt_to보다 앞의 시점이도록 제한 (raise IntegrityError)
        #     models.CheckConstraint(
        #         check=Q('dt_from__lt=dt_to'),  # dt_from less than dt_to
        #         name='period check'
        #     ),
        # )


class JoinRequest(models.Model):
    """
    비공개 그룹에 대한 그룹 가입 요청
    - JoinRequest : SystemUser = N : 1 (여러 그룹에 가입 요청을 할 수 있음)
    - JoinRequest : Group = N : 1 (한 그룹은 여러 그룹 요청을 받을 수 있음)
    """
    created_at = models.DateTimeField('요청 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='arrived_join_requests')
    user = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                             verbose_name='신청 유저', related_name='send_join_requests')

    class Meta:
        verbose_name = '그룹 가입 요청'
        verbose_name_plural = '그룹 가입 요청 목록'

        constraints = (
            # 그룹에 한 번만 가입 요청을 할 수 있음
            models.UniqueConstraint(
                fields=['group', 'user'],
                name='single join request',
            ),
        )
