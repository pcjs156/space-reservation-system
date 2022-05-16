from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from commons.views import handler_500_view
from reservations.models import Term, Space, Reservation
from users.models import PermissionTag
from users.views import ManagerOnlyView, MemberOnlyView


class TermListView(ManagerOnlyView):
    """
    그룹에 등록된 약관 목록을 조회하는 View
    """

    def get(self, request, *args, **kwargs):
        registered_terms = self.group.registered_terms.all()
        self.context['registered_terms'] = registered_terms

        return render(request, 'reservations/term_list.html', self.context)


class TermCreateView(ManagerOnlyView):
    """
    약관 생성을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'reservations/term_create.html', self.context)

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        body = request.POST['body']

        Term.objects.create(group=self.group, title=title, body=body)

        return redirect('reservations:term_list', group_pk=self.group.pk)


class TermDeleteView(ManagerOnlyView, Term.FindingSingleInstance):
    """
    약관 삭제를 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_term(request, *args, **kwargs)
        self.target_term.delete()
        return redirect('reservations:term_list', group_pk=self.group.pk)


class TermUpdateView(ManagerOnlyView, Term.FindingSingleInstance):
    """
    약관 갱신을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_term(request, *args, **kwargs)
        return render(request, 'reservations/term_update.html', self.context)

    def post(self, request, *args, **kwargs):
        self.init_term(request, *args, **kwargs)

        new_title = request.POST['title']
        new_body = request.POST['body']

        self.target_term.title = new_title
        self.target_term.body = new_body
        self.target_term.save()

        return redirect('reservations:term_list', group_pk=self.group.pk)


class SpaceListView(MemberOnlyView):
    """
    그룹에 등록된 공간 목록을 보여주는 View
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'reservations/space_list.html', self.context)


class SpaceDetailView(MemberOnlyView, Space.FindingSingleInstance):
    """
    그룹에 등록된 공간의 세부 정보 및 예약 정보를 보여주는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)

        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')

        target_day = Reservation.get_datetime(year, month, day)
        if target_day is None:
            raise Http404()

        reservation_of_week = Reservation.get_reservation_of_week(target_day, self.space)
        self.context['reservation_of_week'] = reservation_of_week
        self.context['hour_24'] = list(range(24))
        self.context['weekday_7'] = list(range(7))

        time_index = [
            ('AM' if i < 12 else 'PM') +
            '{:0>2s}'.format(str(i if i <= 12 else i % 12)) + ':00' for i in range(24)
        ]
        self.context['time_index'] = time_index

        monday = target_day - timezone.timedelta(days=target_day.weekday())
        sunday = monday + timezone.timedelta(days=7)
        self.context['monday'] = monday
        self.context['sunday'] = sunday
        self.context['monday_dt'] = monday.strftime('%Y/%m/%d')
        self.context['sunday_dt'] = sunday.strftime('%Y/%m/%d')

        prev_monday = monday - timezone.timedelta(days=7)
        self.context[
            'prev_monday_querystring'] = f"year={prev_monday.year}&month={prev_monday.month}&day={prev_monday.day}"
        next_monday = monday + timezone.timedelta(days=7)
        self.context[
            'next_monday_querystring'] = f"year={next_monday.year}&month={next_monday.month}&day={next_monday.day}"

        today = timezone.now()
        self.context['today_querystring'] = f"year={today.year}&month={today.month}&day={today.day}"

        return render(request, 'reservations/space_detail.html', self.context)


class SpaceCreateView(ManagerOnlyView):
    """
    공간 생성을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        terms = self.group.registered_terms.all()
        self.context['terms'] = terms

        permission_tags = self.group.registered_permission_tags.all()
        self.context['permission_tags'] = permission_tags

        return render(request, 'reservations/space_create.html', self.context)

    def post(self, request, *args, **kwargs):
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
            group=self.group, term=term, name=name,
            term_body='' if term is None else term.body,
            required_permission=permission_tag
        )

        return redirect('reservations:space_list', group_pk=self.group.pk)


class SpaceUpdateView(ManagerOnlyView, Space.FindingSingleInstance):
    """
    공간에 대한 정보의 갱신을 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)

        terms = self.group.registered_terms.all()
        self.context['terms'] = terms
        self.context['current_term'] = self.space.term

        permission_tags = self.group.registered_permission_tags.all()
        self.context['permission_tags'] = permission_tags
        self.context['current_permission_tag'] = self.space.required_permission

        return render(request, 'reservations/space_update.html', self.context)

    def post(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)

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

        self.space.name = new_name
        self.space.term = new_term
        self.space.required_permission = new_permission_tag
        self.space.save()

        return redirect('reservations:space_detail', group_pk=self.group.pk, space_pk=self.space.pk)


class SpaceDeleteView(ManagerOnlyView, Space.FindingSingleInstance):
    """
    공간 삭제를 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)
        self.space.delete()
        return redirect('reservations:space_list', group_pk=self.group.pk)


class CreateReservationView(MemberOnlyView, Space.FindingSingleInstance):
    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)
        self.context['blocked'] = False
        self.context['permission_rejected'] = False

        valid_blocks = request.user.get_valid_blocks_in_group(self.group)
        # 현재 사용 제한이 걸린 경우
        if valid_blocks:
            self.context['blocked'] = True
            self.context['valid_blocks'] = valid_blocks
            return render(request, 'reservations/reservation_create.html', self.context)
        # 사용 권한이 만족되지 않은 경우
        elif self.space.required_permission is not None and \
                self.space.required_permission not in request.user.get_permission_tags_in_group(self.group):
            self.context['permission_rejected'] = True
            return render(request, 'reservations/reservation_create.html', self.context)

        # 월요일, 그리고 월요일부터 몇일 만큼 떨어진 요일인지를 기준으로 time table을 렌더링함
        monday_year = request.GET.get('monday_year')
        monday_month = request.GET.get('monday_month')
        monday_day = request.GET.get('monday_day')
        wd = int(request.GET.get('wd', 0))
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
        # 이미 예약되어 있는 경우
        if Reservation.objects.filter(space=self.space, dt_from__gte=target_dt,
                                      dt_to__lt=target_dt + timezone.timedelta(hours=1)).exists():
            self.context['already_booked'] = True
        else:
            self.context['already_booked'] = False

            self.context['reservation_year'] = target_dt.year
            self.context['reservation_month'] = target_dt.month
            self.context['reservation_day'] = target_dt.day
            self.context['reservation_hour'] = hour
            self.context['reservation_weekday'] = '월화수목금토일'[target_dt.weekday()]

        return render(request, 'reservations/reservation_create.html', self.context)

    def post(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)

        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        day = int(request.POST.get('day'))
        hour = int(request.POST.get('hour'))

        # 이미 예약되어 있는 경우
        target_dt = timezone.datetime(year, month, day, hour)
        if Reservation.objects.filter(space=self.space,
                                      dt_from__gte=target_dt,
                                      dt_to__lt=target_dt + timezone.timedelta(hours=1)):
            self.context['already_booked'] = True
            self.get(request, *args, **kwargs)
        # 정상 예약
        else:
            new_reservation = Reservation.objects.create(space=self.space, member=request.user,
                                                         promised_term_body='' if self.space.term is None else self.space.term.body,
                                                         dt_from=target_dt,
                                                         dt_to=target_dt + timezone.timedelta(minutes=59))
            return redirect('reservations:reservation_detail',
                            group_pk=self.group.pk, space_pk=self.space.pk, reservation_pk=new_reservation.pk)


class ReservationDetailView(MemberOnlyView, Space.FindingSingleInstance, Reservation.FindingSingleInstance):
    """
    예약 한 건에 대한 상세 정보 조회를 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)
        self.init_reservation(request, *args, **kwargs)
        return render(request, 'reservations/reservation_detail.html', self.context)


class ReservationDeleteView(MemberOnlyView, Space.FindingSingleInstance):
    """
    예약 삭제를 수행하는 View
    """

    def get(self, request, *args, **kwargs):
        self.init_space(request, *args, **kwargs)

        reservation_pk = int(kwargs['reservation_pk'])
        if request.user == self.group.manager:
            reservation = get_object_or_404(Reservation, space=self.space, pk=reservation_pk)
        else:
            reservation = get_object_or_404(Reservation, space=self.space, pk=reservation_pk, member=request.user)
        reservation.delete()

        return redirect('reservations:space_detail', group_pk=self.group.pk, space_pk=self.space.pk)
