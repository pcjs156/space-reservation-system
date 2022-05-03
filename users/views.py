from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


def login_view(request, *args, **kwargs):
    if request.method == 'GET':
        return render(request, 'users/login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('config:main')
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
    return redirect('config:main')
