import string
import random
from typing import Union, List

from django.db import models, IntegrityError, transaction
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinLengthValidator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone


class SystemUser(AbstractUser):
    """
    시스템 사용자
    - SystemUser : Group = 1 : 1 (그룹 매니저)
    - SystemUser : JoinRequest = 1 : N (여러 그룹에 가입 요청을 할 수 있음)
    - SystemUser : Group = N : M (사용자는 여러 그룹에 가입할 수 있고, 그룹은 여러 사용자를 포함할 수 있음)
    """
    # (Not inherit)
    first_name = None
    last_name = None

    nickname = models.CharField('닉네임', max_length=30, blank=False, null=False)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    @classmethod
    def signup(cls, username: str, password: str, email: str, nickname: str) -> 'SystemUser':
        """
        새 유저를 생성해 반환하는 메서드
        :param username: 사용할 username (unique)
        :param password: 사용할 password
        :param email: 사용할 email (unique)
        :param nickname: 사용할 nickname
        :return: 생성된 SystemUser instance
        :raises IntegrityError: unique constraint 위반시
        """
        user = cls.objects.create(
            username=username, email=email, nickname=nickname
        )
        user.set_password(password)
        user.save()
        return user

    def update_info(self, *args, **kwargs) -> None:
        """
        인자를 입력받아 사용자의 정보를 갱신하는 메서드
        """
        if kwargs.get('nickname'):
            self.nickname = kwargs['nickname']

        self.save()

    def classify_group_list(self) -> [List[Group], List[Group]]:
        """
        해당 사용자가 소속된 그룹을 매니저로써/멤버로써의 소속으로 나누어 각각 반환하는 메서드
        :return: [매니저로 소속된 그룹의 목록, 멤버로 소속된 그룹의 목록]
        """
        # 해당 사용자가 소속된 그룹을 모두 가져옴
        _groups = self.belonged_groups.all()

        # 그룹 매니저로 등록되어 있는 그룹은 따로 보여주어야 함
        groups_as_manager = list()
        # 그룹 매니저로 등록되어 있지 않은 그룹도 따로 분리함
        groups_as_member = list()

        for group in _groups:
            if group.manager == self:
                groups_as_manager.append(group)
            else:
                groups_as_member.append(group)

        return groups_as_manager, groups_as_member

    def get_permission_tags_in_group(self, group: Group) -> List[Group]:
        """
        그룹 내에 등록된 모든 Permission Tag들을 반환하는 메서드
        :param group: 검색 대상 그룹
        :return: group 내에서 해당 멤버에게 주어진 PermissionTag 목록
        """
        return self.given_permission_tags.filter(group=group)

    def update_permission_tags(self, group: Group, permission_tag_str: str) -> List[Group]:
        """
        권한 문자열을 전달받아 해당 그룹 내에서의 권한을 갱신하는 메서드
        :param group: 대상 그룹
        :param permission_tag_str: 갱신에 사용할 권한 문자열(space-bar separated)
        :return: 갱신 후 해당 사용자에게 부여된 그룹 내에서의 권한 목록
        """
        tag_bodies = permission_tag_str.split()

        with transaction.atomic():
            # 갱신 이전에 사용자에게 종속된 Permission tag들을 기록해놓음
            prev_tags = set(self.target_member.get_permission_tags_in_group(self.group))

            for body in tag_bodies:
                tag, is_created = PermissionTag.objects.get_or_create(group=self.group, body=body)

                # 새로 생성된 태그인 경우 멤버와 연결해줌
                if is_created:
                    tag.members.add(self.target_member)
                    tag.save()
                else:
                    # 원래 멤버가 사용하던 태그는 prev_tags에서 지워줌
                    # (남은 태그들 중 해당 멤버만 사용하던 태그가 있으면 삭제할 것)
                    if tag in prev_tags:
                        prev_tags.remove(tag)
                    else:
                        tag.members.add(self.target_member)

            # 더이상 사용하지 않는 태그에서 해당 멤버를 삭제
            for tag in prev_tags:
                tag.members.remove(self.target_member)
                tag.save()

        # 갱신 후 다시 조회하여 반환함
        return self.get_permission_tags_in_group(group)

    def get_entire_blocks_in_group(self, group: Group) -> List['Block']:
        """
        그룹 내에 등록된 모든 Block 내역을 반환하는 메서드
        :param group: 검색 대상 그룹
        :return: group 내에서 해당 멤버에게 주어진 Block 목록
        """
        return self.blocks.filter(group=group)

    def get_valid_blocks_in_group(self, group: Group) -> List['Block']:
        """
        그룹 내에 등록된 현시점에서 유효한 Block 내역을 반환하는 메서드
        :param group: 검색 대상 그룹
        :return: group 내에서 해당 멤버에게 주어진 유효한 Block 목록
        """

        entire_blocks = self.get_entire_blocks_in_group(group)
        now = timezone.now()
        valid_blocks = entire_blocks.filter(dt_from__lte=now, dt_to__gte=now)

        return valid_blocks


class Group(models.Model):
    """
    여러 사용자를 포함하는 그룹
    - Group : SystemUser = 1 : 1 (그룹 매니저)
    - Group : SystemUser = 1 : N (그룹에 다수의 멤버가 소속될 수 있음)
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

    def update_info(self, *args, **kwargs) -> None:
        """
        인자를 입력받아 그룹의 정보를 갱신하는 메서드
        """
        if kwargs.get('name'):
            self.name = kwargs['name']

        if kwargs.get('is_public'):
            # 비공개 상태에서 공개 상태로 수정하려는 경우, 모든 가입 요청을 수락한다.
            if not self.group.is_public and kwargs.get('is_public'):
                for join_request in self.group.arrived_join_requests.all():
                    join_request.accept()

        if kwargs.get('manager'):
            new_manager = self.member_check(kwargs['manager'])
            self.manager = new_manager

        self.save()

    def handover_group_manager(self, target_user: SystemUser) -> None:
        """
        그룹 매니저 권한을 다른 멤버에게 위임하는 메서드
        :param target_user: 매니저 권한을 양도할 대상 멤버
        """
        self.update_info(manager=target_user)

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

    def remove_member(self, user: SystemUser):
        """
        그룹으로부터 멤버를 삭제하는 메서드
        :param user: .삭제할 멤버
        """
        assert self.members.filter(pk=user.pk).exists()
        assert self.manager != user

        with transaction.atomic():
            # 권한 태그에서 사용자 삭제
            for permission_tag in self.registered_permission_tags.all():
                if permission_tag.members.filter(pk=user.pk).exists():
                    permission_tag.members.remove(user)
                    permission_tag.save()

            # 그룹에서 사용자 삭제
            self.members.remove(user)

    def member_check(self, user: Union[SystemUser, int]) -> SystemUser:
        """
        인자로 전달된 사용자(또는 사용자의 pk로 검색한 SystemUser)가 해당 그룹의 멤버인지 확인하는 메서드
        :param user: SystemUser instance or instances'pk
        :return: 인자로 전달된 member instance, 또는 해당 pk를 가지는 member instance
        """
        if isinstance(user, int):
            user = get_object_or_404(SystemUser, pk=user)

        try:
            user = self.members.get(pk=user.pk)
        except SystemUser.DoesNotExist:
            raise Http404()

        return user


class PermissionTag(models.Model):
    """
    그룹 내에서의 권한을 표시하기 위한 태그
    해당 태그의 존재 여부로 그룹 사용자의 특정 기능의 사용 가능 여부가 정해진다.
    - PermissionTag : SystemUser = N : M (여러 사용자가 여러 권한을 가질 수 있으므로)
    - PermissionTag : Group = N : 1 (권한은 그룹 안에서 유효하므로)
    """
    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='registered_permission_tags')
    members = models.ManyToManyField(SystemUser,
                                     verbose_name='대상 멤버', related_name='given_permission_tags')
    body = models.CharField(max_length=10, blank=False, null=False)

    class Meta:
        verbose_name = '권한 태그'
        verbose_name_plural = '권한 태그 목록'
        constraints = (
            # 그룹 내의 모든 tag는 서로 다른 body를 가지고 있음
            models.UniqueConstraint(
                fields=['group', 'body'],
                name='unique permission tag in group',
            ),
        )


class Block(models.Model):
    """
    그룹 내 활동 제한 내역
    - Block : SystemUser = N : 1 (한 사용자가 여러 번 제한될 수 있으므로)
    - Block : Group : N : 1 (한 그룹에 여러 건의 제한이 있을 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='blocks_in_group')
    member = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                               verbose_name='대상 멤버', related_name='blocks')
    dt_from = models.DateTimeField('제한 시작 일시', blank=False, null=False)
    dt_to = models.DateTimeField('제한 해제 일시', blank=False, null=False)

    class Meta:
        verbose_name = '제한 내역'
        verbose_name_plural = '제한 내역'


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

    def accept(self):
        self.group.members.add(self.user)
        self.group.save()
        self.delete()

    def reject(self):
        self.delete()
