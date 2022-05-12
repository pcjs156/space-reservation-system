from django.shortcuts import render, get_object_or_404

from reservations.models import Term
from users.decorators import group_manager_only


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
