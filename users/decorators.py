from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from users.models import Group


def anonymous_user_only(func):
    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:request_logout')
        else:
            return func(request, *args, **kwargs)

    return decorated


def group_member_only(func):
    @login_required
    def decorated(request, *args, **kwargs):
        # 그룹 멤버 검사
        pk = kwargs.get('pk')
        group = get_object_or_404(Group, pk=pk)
        if not group.members.contains(request.user):
            raise Http404()

        kwargs['group'] = group

        return func(request, *args, **kwargs)

    return decorated


def group_manager_only(func):
    @group_member_only
    def decorated(request, *args, **kwargs):
        # 그룹 매니저 검사
        if kwargs['group'].manager != request.user:
            raise Http404()
        else:
            return func(request, *args, **kwargs)

    return decorated
