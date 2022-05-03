from django.shortcuts import redirect


def anonymous_user_only(func):
    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:request_logout')
        else:
            return func(request, *args, **kwargs)

    return decorated
