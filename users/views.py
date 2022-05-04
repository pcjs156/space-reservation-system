from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from utils.validation import check_not_null
from .decorators import anonymous_user_only
from .models import SystemUser


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
