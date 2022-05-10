import member as member
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from utils.validation import check_not_null

from .decorators import anonymous_user_only, group_manager_only, group_member_only
from .models import SystemUser, Group, JoinRequest
from .utils import sort_group_member


@anonymous_user_only
def login_view(request, *args, **kwargs):
    if request.method == 'GET':
        return render(request, 'users/login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/?toastType=login')
        else:
            context = dict()
            error_message = None

            if username is None or password is None:
                error_message = 'ID와 Password를 모두 입력해 주세요.'
            elif user is None:
                error_message = 'ID 또는 Password가 틀렸습니다.'

            assert error_message is not None
            context['error_message'] = error_message

            return render(request, 'users/login.html', context)


@login_required
def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('commons:main')


@login_required
def request_logout_view(request, *args, **kwargs):
    return render(request, 'users/request_logout.html')


@anonymous_user_only
def signup_view(request, *args, **kwargs):
    if request.method == 'GET':
        return render(request, 'users/signup.html')
    elif request.method == 'POST':
        context = dict()

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')

        if not check_not_null(username, password, email, nickname):
            context['error_message'] = '모든 필드를 입력해 주세요.'
        else:
            try:
                user = SystemUser.objects.create(
                    username=username, email=email, nickname=nickname
                )
                user.set_password(password)
                user.save()
            except IntegrityError as e:
                if SystemUser.objects.filter(username=username).exists():
                    context['error_message'] = '이미 사용중인 ID입니다.'
                elif SystemUser.objects.filter(email=email).exists():
                    context['error_message'] = '이미 사용중인 Email입니다.'
                else:
                    context['error_message'] = 'E01: 관리자에게 문의해주세요.'
            except Exception as e:
                context['error_message'] = str(e)

        if context.get('error_message'):
            return render(request, 'users/signup.html', context)
        else:
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/?toastType=signUp')


@login_required
def modify_info_view(request, *args, **kwargs):
    context = dict()

    if request.method == 'GET':
        context['modify_requested'] = False
        return render(request, 'users/modify_account_info.html')

    elif request.method == 'POST':
        context['modify_requested'] = True

        new_nickname = request.POST.get('nickname')
        if not new_nickname:
            context['modify_failed'] = True
            context['toast_message'] = 'Nickname is empty.'
        else:
            request.user.nickname = new_nickname
            request.user.save()
            context['modify_failed'] = False
            context['toast_message'] = 'Modified!'

        return render(request, 'users/modify_account_info.html', context)


@login_required
def group_list_view(request, *args, **kwargs):
    context = dict()
    context['group_create_failed'] = False

    # 그룹 생성 요청이 들어온 경우
    if request.method == 'POST':
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') == 'y'

        try:
            new_group = Group.start_new_group(request.user, name, is_public)
        except IntegrityError:
            context['group_create_failed'] = True
            context['group_create_fail_message'] = 'Try another group name.'
        except Exception as e:
            context['group_create_failed'] = True
            context['group_create_fail_message'] = 'You can manage only 50 groups.'
        else:
            context['group_create_failed'] = False
            context['created_group'] = new_group

    # 해당 사용자가 소속된 그룹을 모두 가져옴
    _groups = request.user.belonged_groups.all()

    # 그룹 매니저로 등록되어 있는 그룹은 따로 보여주어야 함
    groups_as_manager = list()
    # 그룹 매니저로 등록되어 있지 않은 그룹도 따로 분리함
    groups_as_member = list()

    for group in _groups:
        if group.manager == request.user:
            groups_as_manager.append(group)
        else:
            groups_as_member.append(group)

    context['groups_as_manager'] = groups_as_manager
    context['groups_as_member'] = groups_as_member

    return render(request, 'users/group_list.html', context)


@group_member_only
def group_detail_view(request, *args, **kwargs):
    context = dict()
    group = kwargs['group']
    context['group'] = group

    members = list(group.members.all())
    sort_group_member(group, members, True)

    member_infos = [
        {
            'username': _member.username,
            'nickname': _member.nickname,
            'permission_tags': _member.get_permission_tags_in_group(group),
            'blocked': len(_member.get_valid_blocks_in_group(group)) > 0,
            'is_manager': _member == group.manager,
        } for _member in members
    ]
    context['member_infos'] = member_infos

    # 그룹 매니저인 경우 그룹 관리 기능 활성화
    if group.manager == request.user:
        context['join_requests'] = group.arrived_join_requests.all()

    return render(request, 'users/group_detail.html', context)


@group_manager_only
def group_manage_view(request, *args, **kwargs):
    context = dict()

    group = kwargs['group']
    context['group'] = group

    if request.method == 'GET':
        return render(request, 'users/group_manage.html', context)
    elif request.method == 'POST':
        name = request.POST.get('name')
        is_public = request.POST.get('is_public') is not None

        context['is_modify_failed'] = False

        try:
            group.name = name
            group.is_public = is_public
            group.save()
        except IntegrityError:
            context['is_modify_failed'] = True
            context['modify_fail_message'] = 'This group name is already used.'

        return render(request, 'users/group_manage.html', context)


@group_manager_only
def group_delete_view(request, *args, **kwargs):
    group = kwargs['group']
    group.delete()

    del kwargs['group']

    return redirect('users:group')


@group_manager_only
def group_invite_code_change_view(request, *args, **kwargs):
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


@login_required
def group_search_view(request, *args, **kwargs):
    invite_code = request.GET.get('invite_code')

    context = dict()

    if invite_code:
        try:
            group = Group.objects.get(invite_code=invite_code)
        except Group.DoesNotExist:
            context['search_complete'] = False
        else:
            context['search_complete'] = True
            context['group'] = group

    return render(request, 'users/group_search.html', context)


@login_required
def group_join_request(request, *args, **kwargs):
    if request.method == 'GET':
        return render(request, 'users/group_join_request.html')
    elif request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        group = get_object_or_404(Group, invite_code=invite_code)

        context = dict()
        context['group'] = group

        # 이미 가입한 그룹인 경우
        if request.user.belonged_groups.filter(pk=group.pk).exists():
            context['already_member'] = True
        # 가입하지 않은 그룹인 경우
        else:
            context['already_member'] = False
            context['already_requested'] = False

            # 공개된 그룹인 경우 바로 멤버로 등록됨
            if group.is_public:
                group.members.add(request.user)
                group.save()
            # 공개되지 않은 그룹인 경우 그룹 등록 요청을 보냄
            else:
                try:
                    join_request = JoinRequest.objects.create(group=group, user=request.user)
                    context['join_request'] = join_request
                # 한 그룹에 한 번만 가입 요청을 할 수 있음
                except IntegrityError:
                    context['already_requested'] = True

        return render(request, 'users/group_join_request.html', context)


@group_member_only
def group_member_detail_view(request, *args, **kwargs):
    group = kwargs['group']
    member_pk = kwargs['member_pk']

    _try_withdraw = kwargs.get('_try_withdraw', False)
    _withdraw_errormessage = kwargs.get('_withdraw_errormessage', False)

    context = dict()
    context['group'] = group

    if _try_withdraw:
        context['try_withdraw'] = True
        context['try_withdraw_errormessage'] = _withdraw_errormessage

    target_member = get_object_or_404(SystemUser, pk=member_pk)

    # 조회/수정의 목표가 되는 사용자가 해당 그룹에 존재하며, 요청한 본인이 아닌 경우 404 error
    if not (group.members.filter(pk=member_pk) and request.user == target_member):
        raise Http404()

    return render(request, 'users/group_member_detail.html', context)


@group_member_only
def group_withdraw_view(request, *args, **kwargs):
    group = kwargs['group']
    member_pk = kwargs['member_pk']

    target_member = get_object_or_404(SystemUser, pk=member_pk)
    # 조회/수정의 목표가 되는 사용자가 해당 그룹에 존재하며, 요청한 본인이 아닌 경우 404 error
    if not (group.members.filter(pk=member_pk) and request.user == target_member):
        raise Http404()

    # 그룹의 매니저는 탈퇴할 수 없음
    # 다시 멤버 정보 페이지로 돌려보냄
    if group.manager == request.user:
        kwargs['_try_withdraw'] = True
        kwargs['_withdraw_errormessage'] = "Manager can't exit from group."
        return group_member_detail_view(request, *args, **kwargs)
    else:
        group.remove_member(request.user)
        return redirect('users:group')


@group_manager_only
def accept_join_request_view(request, *args, **kwargs):
    target_user_pk = kwargs['user_pk']
    join_request_pk = kwargs['request_pk']

    group = kwargs['group']
    user = get_object_or_404(SystemUser, pk=target_user_pk)
    join_request = get_object_or_404(JoinRequest, pk=join_request_pk, user=user, group=group)
    join_request.accept()

    return group_detail_view(request, *args, **kwargs)


@group_manager_only
def reject_join_request_view(request, *args, **kwargs):
    target_user_pk = kwargs['user_pk']
    join_request_pk = kwargs['request_pk']

    group = kwargs['group']
    user = get_object_or_404(SystemUser, pk=target_user_pk)
    join_request = get_object_or_404(JoinRequest, pk=join_request_pk, user=user, group=group)
    join_request.reject()

    return group_detail_view(request, *args, **kwargs)
