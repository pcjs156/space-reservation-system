from django.db import IntegrityError, transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator
from django.views import View

from commons.views import ViewWithContext
from utils.validation import check_not_null

from .decorators import anonymous_user_only, group_manager_only, group_member_only
from .models import SystemUser, Group, JoinRequest, PermissionTag, Block
from .utils import sort_group_member


@method_decorator(group_member_only, name='dispatch')
class ViewWithContextAndGroup(ViewWithContext):
    """
    상속 받는 class-based view의 kwargs와 context에 group을 자동으로 추가해주는 view
    """

    def dispatch(self, request, *args, **kwargs):
        self.group = kwargs['group']
        self.context['group'] = self.group
        return super(ViewWithContextAndGroup, self).dispatch(request, *args, **kwargs)


@method_decorator(group_member_only, name='dispatch')
class MemberOnlyView(ViewWithContextAndGroup):
    """
    ViewWithContextAndGroup에 그룹 멤버 권한 검사가 추가된 뷰
    """

    def __init__(self, *args, **kwargs):
        super(MemberOnlyView, self).__init__(*args, **kwargs)
        if 'group' in kwargs.keys():
            self.group = kwargs['group']


@method_decorator(group_manager_only, name='dispatch')
class ManagerOnlyView(ViewWithContextAndGroup):
    """
    ViewWithContextAndGroup에 매니저 권한 검사가 추가된 뷰
    """
    pass


@method_decorator(anonymous_user_only, name='dispatch')
class LoginView(ViewWithContext):
    """
    로그인 처리 뷰
    """

    def get(self, request, *args, **kwargs):
        """
        로그인 페이지 렌더링
        """
        return render(request, 'users/login.html')

    def post(self, request, *args, **kwargs):
        """
        로그인 처리
        - username : 로그인할 사용자의 ID
        - password : 로그인할 사용자의 비밀번호
        => 로그인 성공 : main_view
        => 로그인 실패 : login_view
        """
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        # 로그인 성공
        if user:
            login(request, user)
            return redirect('/?toastType=login')
        # 로그인 실패
        else:
            error_message = None

            # 로그인 실패 사유 응답
            if username is None or password is None:
                error_message = 'ID와 Password를 모두 입력해 주세요.'
            elif user is None:
                error_message = 'ID 또는 Password가 틀렸습니다.'

            self.context['error_message'] = error_message

            return render(request, 'users/login.html', self.context)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    """
    로그아웃 처리를 수행하는 뷰
    """

    def get(self, request, *args, **kwargs):
        """
        로그아웃 처리
        => 성공/실패 여부와 관계없이 main_view로 redirect됨
        """
        logout(request)
        return redirect('commons:main')


@method_decorator(login_required, name='dispatch')
class RequestLogoutView(View):
    """
    로그인한 사용자가 AnonymousUser만 접근할 수 있는 view에 접근할 경우,
    해당 view로 redirect 되어 logout 요청을 받음
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'users/request_logout.html')


@method_decorator(anonymous_user_only, name='dispatch')
class SignupView(View):
    """
    회원가입 뷰
    """

    def get(self, request, *args, **kwargs):
        """
        회원가입 페이지 렌더링
        """
        return render(request, 'users/signup.html')

    def post(self, request, *args, **kwargs):
        """
        회원가입 처리
        - username: 사용할 ID (unique)
        - password: 사용할 password
        - email: 사용할 email (unique)
        - nickname: 사용할 nickname
        => 성공 : 로그인 처리 후 main page로 이동
        => 이미 사용중인 username/email가 전달될 경우 : 다시 signup page로 이동
        """
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')

        if not check_not_null(username, password, email, nickname):
            self.context['error_message'] = '모든 필드를 입력해 주세요.'
        else:
            try:
                user = SystemUser.signup(username=username, password=password, email=email, nickname=nickname)
            except IntegrityError as e:
                if SystemUser.objects.filter(username=username).exists():
                    self.context['error_message'] = '이미 사용중인 ID입니다.'
                elif SystemUser.objects.filter(email=email).exists():
                    self.context['error_message'] = '이미 사용중인 Email입니다.'
                else:
                    self.context['error_message'] = 'E01: 관리자에게 문의해주세요.'
            except Exception as e:
                self.context['error_message'] = str(e)

        if self.context.get('error_message'):
            return render(request, 'users/signup.html', self.context)
        else:
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/?toastType=signUp')


@method_decorator(login_required, name='dispatch')
class ModifyAccountInfoView(ViewWithContext):
    """
    회원 정보 수정 뷰
    """

    def get(self, request, *args, **kwargs):
        """
        페이지 렌더링
        """
        self.context['modify_requested'] = False
        return render(request, 'users/modify_account_info.html', self.context)

    def post(self, request, *args, **kwargs):
        """
        회원 정보 수정 처리
        - nickname: 변경할 새 닉네임
        => 성공/실패 : 해당 뷰의 get method로 호출되지만, 수행 결과가 메시지로 표시됨
        """
        self.context['modify_requested'] = True

        new_nickname = request.POST.get('nickname')
        if not new_nickname:
            self.context['modify_failed'] = True
            self.context['toast_message'] = 'Nickname is empty.'
        else:
            request.user.update_info(nickname=new_nickname)
            self.context['modify_failed'] = False
            self.context['toast_message'] = 'Modified!'

        return render(request, 'users/modify_account_info.html', self.context)


@method_decorator(login_required, name='dispatch')
class GroupListView(ViewWithContext):
    """
    관리중인 그룹과 소속된 그룹을 분리하여 목록으로 보여주는 뷰
    신규 그룹 생성 기능을 포함한다(POST).
    """

    def __init__(self, *args, **kwargs):
        super(GroupListView, self).__init__(*args, **kwargs)
        self.context['group_create_failed'] = False

    def render_page(self, request, *args, **kwargs):
        """
        생성/조회 요청 상관 없이 항상 그룹 목록을 보여주어야 함
        """
        groups_as_manager, groups_as_member = request.user.classify_group_list()
        self.context['groups_as_manager'] = groups_as_manager
        self.context['groups_as_member'] = groups_as_member

        return render(request, 'users/group_list.html', self.context)

    def get(self, request, *args, **kwargs):
        """
        페이지 렌더링
        """
        return self.render_page(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        그룹 생성 요청
        - name: 그룹명 (unique)
        - is_public: 공개 여부
        => 성공/실패 여부 상관 없이 group list view로 이동된다. (수행 결과를 메시지로 전달받음)
        """
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') == 'y'

        try:
            new_group = Group.start_new_group(request.user, name, is_public)
        except IntegrityError:
            self.context['group_create_failed'] = True
            self.context['group_create_fail_message'] = 'Try another group name.'
        except Exception as e:
            self.context['group_create_failed'] = True
            self.context['group_create_fail_message'] = 'You can manage only 50 groups.'
        else:
            self.context['group_create_failed'] = False
            self.context['created_group'] = new_group

        return self.render_page(request, *args, **kwargs)


class GroupDetailView(ViewWithContextAndGroup):
    """
    그룹, 그룹에 소속된 멤버, 그룹에 등록된 가입 요청을 보여주는 View
    """

    def get(self, request, *args, **kwargs):
        # 속해 있는 모든 멤버를 unique id순으로 정렬하되, manager가 맨위로 오도록 함
        members = list(self.group.members.all())
        sort_group_member(self.group, members, True)

        member_infos = [
            {
                'pk': _member.pk,
                'username': _member.username,
                'nickname': _member.nickname,
                'permission_tags': _member.get_permission_tags_in_group(self.group),
                'blocked': len(_member.get_valid_blocks_in_group(self.group)) > 0,
                'is_manager': _member == self.group.manager,
            } for _member in members
        ]
        self.context['member_infos'] = member_infos

        # 그룹 매니저인 경우 그룹 관리 기능 활성화
        if self.group.manager == request.user:
            self.context['join_requests'] = self.group.arrived_join_requests.all()

        return render(request, 'users/group_detail.html', self.context)


class GroupManageView(ManagerOnlyView):
    """
    그룹 관리 페이지를 처리하는 View
    """

    def get(self, request, *args, **kwargs):
        """
        페이지 렌더링
        """
        return render(request, 'users/group_manage.html', self.context)

    def post(self, request, *args, **kwargs):
        """
        그룹 정보 수정을 처리
        - name: 새 그룹명
        - is_public: 그룹 공개 여부
        => 이미 사용중인 그룹명이 전달될 경우 같은 페이지에서 피드백해줌
        """
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') is not None

        self.context['is_modify_failed'] = False

        try:
            self.group.update_info(name=name, is_public=is_public)
        except IntegrityError:
            self.context['is_modify_failed'] = True
            self.context['modify_fail_message'] = 'This group name is already used.'

        return render(request, 'users/group_manage.html', self.context)


class GroupDeleteView(ManagerOnlyView):
    """
    그룹의 삭제를 수행하는 View
    """

    def post(self, request, *args, **kwargs):
        group = kwargs['group']
        group.delete()

        del kwargs['group']

        return redirect('users:group')


class GroupInviteCodeChangeView(ManagerOnlyView):
    """
    그룹 초대 코드 수정을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        group = kwargs['group']

        while True:
            try:
                new_invite_code = Group.get_unique_invite_code()
                group.invite_code = new_invite_code
                group.save()
            except IntegrityError:
                continue
            else:
                break

        return JsonResponse({'new_invite_code': group.invite_code})


@method_decorator(login_required, name='dispatch')
class GroupSearchView(ViewWithContext):
    """
    그룹 검색을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        invite_code = request.GET.get('invite_code')

        if invite_code:
            try:
                group = Group.objects.get(invite_code=invite_code)
            except Group.DoesNotExist:
                self.context['search_complete'] = False
            else:
                self.context['search_complete'] = True
                self.context['group'] = group

        return render(request, 'users/group_search.html', self.context)


@method_decorator(login_required, name='dispatch')
class GroupJoinRequestView(ViewWithContext):
    """
    그룹 가입 요청을 처리하는 View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'users/group_join_request.html')

    def post(self, request, *args, **kwargs):
        invite_code = request.POST.get('invite_code')
        group = get_object_or_404(Group, invite_code=invite_code)

        self.context['group'] = group

        # 이미 가입한 그룹인 경우
        if request.user.belonged_groups.filter(pk=group.pk).exists():
            self.context['already_member'] = True
        # 가입하지 않은 그룹인 경우
        else:
            self.context['already_member'] = False
            self.context['already_requested'] = False

            # 공개된 그룹인 경우 바로 멤버로 등록됨
            if group.is_public:
                group.members.add(request.user)
                group.save()
            # 공개되지 않은 그룹인 경우 그룹 등록 요청을 보냄
            else:
                try:
                    join_request = JoinRequest.objects.create(group=group, user=request.user)
                    self.context['join_request'] = join_request
                # 한 그룹에 한 번만 가입 요청을 할 수 있음
                except IntegrityError:
                    self.context['already_requested'] = True

        return render(request, 'users/group_join_request.html', self.context)


class AcceptJoinRequestView(ManagerOnlyView):
    """
    그룹 가입 요청을 수락하는 View
    """

    def get(self, request, *args, **kwargs):
        target_user_pk = kwargs['user_pk']
        join_request_pk = kwargs['request_pk']

        target_user = get_object_or_404(SystemUser, pk=target_user_pk)
        join_request = get_object_or_404(JoinRequest, pk=join_request_pk, user=target_user, group=self.group)
        join_request.accept()

        return redirect('users:group_detail', group_pk=self.group.pk)


class RejectJoinRequestView(ManagerOnlyView):
    """
    그룹 가입 요청을 거절하는 View
    """

    def get(self, request, *args, **kwargs):
        target_user_pk = kwargs['user_pk']
        join_request_pk = kwargs['request_pk']

        target_user = get_object_or_404(SystemUser, pk=int(target_user_pk))
        join_request = get_object_or_404(JoinRequest, pk=join_request_pk, user=target_user, group=self.group)
        join_request.reject()

        return redirect('users:group_detail', group_pk=self.group.pk)


class GroupMemberDetailView(MemberOnlyView):
    """
    그룹 멤버 본인의 그룹 내 정보 조회 및 수정을 수행하는 뷰
    """

    def get(self, request, *args, **kwargs):
        member_pk = kwargs['member_pk']

        _try_withdraw = kwargs.get('_try_withdraw', False)
        _withdraw_errormessage = kwargs.get('_withdraw_errormessage', False)

        self.context['group'] = self.group

        if _try_withdraw:
            self.context['try_withdraw'] = True
            self.context['try_withdraw_errormessage'] = _withdraw_errormessage

        # 조회/수정의 목표가 되는 사용자가 해당 그룹에 존재하며, 요청한 본인이 아닌 경우 404 error
        target_member = self.group.member_check(member_pk)
        if request.user != target_member:
            raise Http404()

        return render(request, 'users/group_member_detail.html', self.context)


class GroupWithdrawView(MemberOnlyView):
    """
    그룹 탈퇴를 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        member_pk = kwargs['member_pk']

        # 조회/수정의 목표가 되는 사용자가 해당 그룹에 존재하며, 요청한 본인이 아닌 경우 404 error
        target_member = self.group.member_check(member_pk)
        if request.user != target_member:
            raise Http404()

        # 그룹의 매니저는 탈퇴할 수 없음
        # 다시 멤버 정보 페이지로 돌려보냄
        if self.group.manager == request.user:
            kwargs['_try_withdraw'] = True
            kwargs['_withdraw_errormessage'] = "Manager can't exit from group."
            return GroupMemberDetailView(group=self.group).get(request, *args, **kwargs)
        else:
            self.group.remove_member(request.user)
            return redirect('users:group')


class KickGroupMemberView(ManagerOnlyView):
    """
    그룹 멤버 추방을 수행하는 뷰
    """

    def get(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']

        group = kwargs['group']
        target_member = group.member_check(target_member_pk)
        group.remove_member(target_member)

        return redirect('users:group_detail', group_pk=group.pk)


class GroupMemberPermissionView(ManagerOnlyView):
    """
    그룹 멤버의 권한 조회 및 수정을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)

        self.context['member'] = target_member
        self.context['tag_edit'] = False
        self.context['permission_str'] = ' '.join(
            map(lambda t: t.body, target_member.get_permission_tags_in_group(self.group)))

        return render(request, 'users/group_member_permission.html', self.context)

    def post(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)

        self.context['member'] = target_member
        self.context['tag_edit'] = True

        permission_tag_str = request.POST.get('permission_str', '')
        updated_permission_tags = request.user.updated_permission_tags(self.group, permission_tag_str)

        self.context['permission_str'] = ' '.join(
            map(lambda t: t.body, updated_permission_tags)
        )

        return render(request, 'users/group_member_permission.html', self.context)


class GroupManagerHandoverView(ManagerOnlyView):
    """
    그룹 매니저 권한을 위임하는 View
    """

    def post(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)

        self.group.handover_group_manager(target_member)

        return redirect('users:group_detail', group_pk=self.group.pk)


class BlockListView(ManagerOnlyView):
    """
    멤버별 차단 항목 및 차단 생성 처리 View
    """

    def get(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)
        self.context['member'] = target_member

        valid_blocks = target_member.get_valid_blocks_in_group(self.group)
        self.context['valid_blocks'] = valid_blocks

        return render(request, 'users/block_list.html', self.context)

    def post(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)
        self.context['member'] = target_member

        valid_blocks = target_member.get_valid_blocks_in_group(self.group)
        self.context['valid_blocks'] = valid_blocks

        block_to_time = request.POST.get('block_to_time')
        block_to_date = request.POST.get('block_to_date')

        block_to = dateparse.parse_datetime(block_to_date + 'T' + block_to_time)
        now = timezone.now()

        if now > block_to:
            self.context['past_dt'] = True
            return render(request, 'users/block_list.html', self.context)
        else:
            block = Block.objects.create(group=self.group, member=target_member,
                                         dt_from=now, dt_to=block_to)
            return redirect('users:group_detail', group_pk=self.group.pk)


class BlockDeleteView(ManagerOnlyView):
    """
    제한 내역 삭제를 처리하는 View
    """

    def get(self, request, *args, **kwargs):
        target_member_pk = kwargs['member_pk']
        target_member = self.group.member_check(target_member_pk)
        self.context['member'] = target_member

        block = get_object_or_404(Block, pk=kwargs['block_pk'])
        block.delete()

        return redirect('users:group_member_block', group_pk=self.group.pk, member_pk=target_member_pk)
