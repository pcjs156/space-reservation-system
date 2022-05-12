from django.shortcuts import render, get_object_or_404

from reservations.models import Term, Space
from users.decorators import group_manager_only, group_member_only
from users.models import PermissionTag


@group_manager_only
def term_list_view(request, *args, **kwargs):
    context = dict()
    group = kwargs['group']
    context['group'] = group

    registered_terms = group.registered_terms.all()
    context['registered_terms'] = registered_terms

    return render(request, 'reservations/term_list.html', context)


@group_manager_only
def term_create_view(request, *args, **kwargs):
    context = dict()
    group = kwargs['group']
    context['group'] = group

    if request.method == 'GET':
        return render(request, 'reservations/term_create.html', context)

    elif request.method == 'POST':
        title = request.POST['title']
        body = request.POST['body']

        Term.objects.create(group=group, title=title, body=body)

        return term_list_view(request, *args, **kwargs)


@group_manager_only
def term_delete_view(request, *args, **kwargs):
    target_term = get_object_or_404(Term, pk=kwargs['term_pk'])
    target_term.delete()
    return term_list_view(request, *args, **kwargs)


@group_manager_only
def term_update_view(request, *args, **kwargs):
    target_term = get_object_or_404(Term, pk=kwargs['term_pk'])

    if request.method == 'GET':
        context = dict()

        context['group'] = kwargs['group']
        context['target_term'] = target_term

        return render(request, 'reservations/term_update.html', context)

    elif request.method == 'POST':
        new_title = request.POST['title']
        new_body = request.POST['body']

        target_term = get_object_or_404(Term, pk=kwargs['term_pk'])
        target_term.title = new_title
        target_term.body = new_body
        target_term.save()

        return term_list_view(request, *args, **kwargs)


@group_member_only
def space_list_view(request, *args, **kwargs):
    context = dict()
    context['group'] = kwargs['group']

    return render(request, 'reservations/space_list.html', context)


@group_manager_only
def space_detail_view(request, *args, **kwargs):
    space_pk = kwargs['space_pk']
    space = get_object_or_404(Space, group=kwargs['group'], pk=space_pk)

    group = kwargs['group']

    context = dict()
    context['group'] = group
    context['space'] = space

    return render(request, 'reservations/space_detail.html', context)


@group_manager_only
def space_create_view(request, *args, **kwargs):
    context = dict()
    group = kwargs['group']
    context['group'] = group

    if request.method == 'GET':
        terms = group.registered_terms.all()
        context['terms'] = terms

        permission_tags = group.registered_permission_tags.all()
        context['permission_tags'] = permission_tags

        return render(request, 'reservations/space_create.html', context)

    elif request.method == 'POST':
        term_pk = int(request.POST['term'])
        permission_pk = int(request.POST['permission'])
        name = request.POST['name']

        if term_pk != -1:
            term = get_object_or_404(Term, pk=term_pk)
        else:
            term = None

        if permission_pk != -1:
            permission_tag = get_object_or_404(PermissionTag, pk=permission_pk)
        else:
            permission_tag = None

        Space.objects.create(
            group=group, term=term, name=name,
            term_body='' if term is None else term.body,
            required_permission=permission_tag
        )

        return space_list_view(request, *args, **kwargs)


@group_manager_only
def space_update_view(request, *args, **kwargs):
    context = dict()
    group = kwargs['group']
    context['group'] = group

    space = get_object_or_404(Space, group=group, pk=int(kwargs['space_pk']))
    context['space'] = space

    if request.method == 'GET':
        terms = group.registered_terms.all()
        context['terms'] = terms
        context['current_term'] = space.term

        permission_tags = group.registered_permission_tags.all()
        context['permission_tags'] = permission_tags
        context['current_permission_tag'] = space.required_permission

        return render(request, 'reservations/space_update.html', context)

    elif request.method == 'POST':
        term_pk = int(request.POST['term'])
        permission_pk = int(request.POST['permission'])
        new_name = request.POST['name']

        if term_pk != -1:
            new_term = get_object_or_404(Term, pk=term_pk)
        else:
            new_term = None

        if permission_pk != -1:
            new_permission_tag = get_object_or_404(PermissionTag, pk=permission_pk)
        else:
            new_permission_tag = None

        space.name = new_name
        space.term = new_term
        space.required_permission = new_permission_tag
        space.save()

        return space_detail_view(request, *args, **kwargs)


@group_manager_only
def space_delete_view(request, *args, **kwargs):
    space = get_object_or_404(Space, group=kwargs['group'], pk=int(kwargs['space_pk']))
    space.delete()

    return space_list_view(request, *args, **kwargs)
