from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from commons.views import handler_500_view
from reservations.models import Term, Space, Reservation
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


@group_member_only
def space_detail_view(request, *args, **kwargs):
    space_pk = kwargs['space_pk']
    space = get_object_or_404(Space, group=kwargs['group'], pk=space_pk)

    group = kwargs['group']

    context = dict()
    context['group'] = group
    context['space'] = space

    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')

    target_day = Reservation.get_datetime(year, month, day)
    if target_day is None:
        raise Http404()

    reservation_of_week = Reservation.get_reservation_of_week(target_day, space)
    context['reservation_of_week'] = reservation_of_week
    context['hour_24'] = list(range(24))
    context['weekday_7'] = list(range(7))

    time_index = [
        ('AM' if i < 12 else 'PM') +
        '{:0>2s}'.format(str(i if i <= 12 else i % 12)) + ':00' for i in range(24)
    ]
    context['time_index'] = time_index

    monday = target_day - timezone.timedelta(days=target_day.weekday())
    sunday = monday + timezone.timedelta(days=7)
    context['monday'] = monday
    context['sunday'] = sunday
    context['monday_dt'] = monday.strftime('%Y/%m/%d')
    context['sunday_dt'] = sunday.strftime('%Y/%m/%d')

    prev_monday = monday - timezone.timedelta(days=7)
    context['prev_monday_querystring'] = f"year={prev_monday.year}&month={prev_monday.month}&day={prev_monday.day}"
    next_monday = monday + timezone.timedelta(days=7)
    context['next_monday_querystring'] = f"year={next_monday.year}&month={next_monday.month}&day={next_monday.day}"

    today = timezone.now()
    context['today_querystring'] = f"year={today.year}&month={today.month}&day={today.day}"

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


@group_member_only
def create_reservation_view(request, *args, **kwargs):
    context = dict()
    space_pk = kwargs['space_pk']
    space = get_object_or_404(Space, group=kwargs['group'], pk=space_pk)
    context['space'] = space
    context['group'] = kwargs['group']

    if request.method == 'GET':
        context['blocked'] = False
        context['permission_rejected'] = False

        valid_blocks = request.user.get_valid_blocks_in_group(kwargs['group'])
        if valid_blocks:
            context['blocked'] = True
            context['valid_blocks'] = valid_blocks
            return render(request, 'reservations/reservation_create.html', context)
        elif space.required_permission is not None and \
                space.required_permission not in request.user.get_permission_tags_in_group(kwargs['group']):
            context['permission_rejected'] = True
            return render(request, 'reservations/reservation_create.html', context)

        monday_year = request.GET.get('monday_year')
        monday_month = request.GET.get('monday_month')
        monday_day = request.GET.get('monday_day')
        wd = int(request.GET.get('wd'))
        hour = request.GET.get('hour')

        target_monday = Reservation.get_datetime(monday_year, monday_month, monday_day)
        if target_monday is None:
            raise Http404()
        target_day = target_monday + timezone.timedelta(days=wd)

        try:
            hour = int(hour)
            if hour < 0:
                raise Exception
        except Exception:
            return handler_500_view(request, *args, **kwargs)

        target_dt = target_day.replace(hour=hour, minute=0, second=0, microsecond=0)
        if Reservation.objects.filter(space=space, dt_from__gte=target_dt,
                                      dt_to__lt=target_dt + timezone.timedelta(hours=1)).exists():
            context['already_booked'] = True
        else:
            context['already_booked'] = False

            context['reservation_year'] = target_dt.year
            context['reservation_month'] = target_dt.month
            context['reservation_day'] = target_dt.day
            context['reservation_hour'] = hour
            context['reservation_weekday'] = '월화수목금토일'[target_dt.weekday()]

        return render(request, 'reservations/reservation_create.html', context)
    elif request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        day = int(request.POST.get('day'))
        hour = int(request.POST.get('hour'))

        target_dt = timezone.datetime(year, month, day, hour)
        if Reservation.objects.filter(space=space,
                                      dt_from__gte=target_dt,
                                      dt_to__lt=target_dt + timezone.timedelta(hours=1)):
            context['already_booked'] = True
        else:
            new_reservation = Reservation.objects.create(space=space, member=request.user,
                                                         promised_term_body='' if space.term is None else space.term.body,
                                                         dt_from=target_dt,
                                                         dt_to=target_dt + timezone.timedelta(minutes=59))
            kwargs['reservation_pk'] = new_reservation.pk
            return reservation_detail_view(request, *args, **kwargs)


@group_member_only
def reservation_detail_view(request, *args, **kwargs):
    context = dict()

    reservation_pk = int(kwargs['reservation_pk'])

    space_pk = kwargs['space_pk']
    space = get_object_or_404(Space, pk=space_pk, group=kwargs['group'])

    context['group'] = kwargs['group']
    context['space'] = space
    context['reservation'] = get_object_or_404(Reservation, space=space, pk=reservation_pk)

    return render(request, 'reservations/reservation_detail.html', context)


@group_member_only
def reservation_delete_view(request, *args, **kwargs):
    space_pk = kwargs['space_pk']
    space = get_object_or_404(Space, pk=space_pk, group=kwargs['group'])

    reservation_pk = int(kwargs['reservation_pk'])
    if request.user == kwargs['group'].manager:
        reservation = get_object_or_404(Reservation, space=space, pk=reservation_pk)
    else:
        reservation = get_object_or_404(Reservation, space=space, pk=reservation_pk, member=request.user)
    reservation.delete()

    return space_detail_view(request, *args, **kwargs)
