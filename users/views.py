from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from utils.validation import check_not_null

from .decorators import anonymous_user_only
from .models import SystemUser, Group


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


@login_required
def group_detail_view(request, *args, **kwargs):
    context = dict()

    pk = kwargs['pk']

    group = get_object_or_404(Group, pk=pk)
    context['group'] = group

    return render(request, 'users/group_detail.html', context)
