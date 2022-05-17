from datetime import datetime
from typing import List, Dict

from django.contrib.auth.models import Permission
from django.db import models, IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import Group, SystemUser, PermissionTag


class Term(models.Model):
    """
    공간 예약을 위한 약관
    - Term : Group = N : 1 (한 그룹에 여러 약관이 등록될 수 있으므로)
    - Term : Space = 1 : N (한 약관은 여러 공간에서 사용될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 그룹', related_name='registered_terms')

    title = models.CharField('제목', max_length=255, null=False)
    body = models.TextField('내용', null=False, blank=True)

    class Meta:
        verbose_name = '약관'
        verbose_name_plural = '약관 목록'

    class FindingSingleInstance:
        def init_term(self, request, *args, **kwargs):
            target_term = get_object_or_404(Term, pk=kwargs['term_pk'])
            self.term = target_term
            self.context['term'] = self.term

    @classmethod
    def create_term(cls, group: Group, title: str, body: str) -> 'Term':
        """
        새 term instance를 생성해 반환하는 메서드
        :param group: 약관을 등록할 그룹
        :param title: 약관명
        :param body: 약관 본무
        :return: 생성된 새 약관
        """
        return cls.objects.create(group=group, title=title, body=body)

    def update(self, **kwargs) -> None:
        """
        인자를 전달받아 term instance의 정보를 수정하는 메서드
        그룹 정보의 수정은 지원하지 않는다.
        """
        if 'title' in kwargs.keys():
            self.title = kwargs['title']
        if 'body' in kwargs.keys():
            self.body = kwargs['body']

        self.save()


class Space(models.Model):
    """
    예약의 대상이 되는 공간
    - Space : Group = N : 1 (한 그룹에 여러 공간이 등록될 수 있으므로)
    - Space : Term = N : 1 (한 약관이 여러 공간에서 사용될 수 있으므로)
    - Space : PermissionTag = N : 1 (한 권한 태그가 여러 공간에서 요구될 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE,
                              verbose_name='소속 그룹', related_name='registered_spaces')

    term = models.ForeignKey(Term, null=True, on_delete=models.CASCADE,
                             verbose_name='등록 약관', related_name='using_spaces')

    name = models.CharField('공간 이름', max_length=255)

    # term과의 연결은 유지하되, Term의 내용이 변경되었을 때 선택적으로 내용을
    # Space instance에 반영할 수 있도록 구현
    term_body = models.TextField('약관 본문', null=True, blank=True)

    required_permission = models.ForeignKey(PermissionTag, on_delete=models.CASCADE, null=True,
                                            related_name='requiring_spaces', verbose_name='요구 권한')

    class Meta:
        verbose_name = '공간'
        verbose_name_plural = '공간 목록'

    class FindingSingleInstance:
        def init_space(self, request, *args, **kwargs):
            target_space = get_object_or_404(Space, pk=kwargs['space_pk'])
            self.space = target_space
            self.context['space'] = self.space

    @classmethod
    def create_space(cls, name: str, group: Group, term: Term, required_permission: PermissionTag) -> 'Space':
        """
        새 space instance를 생성해 반환하는 메서드
        :param name: 공간명
        :param group: 공간을 등록할 그룹
        :param term: 공간에 등록할 약관
        :param required_permission: 공간에서 예약을 하기 위해 필요한 권한
        :return: 생성된 새 공간
        """
        new_space = cls.objects.create(
            group=group, term=term, name=name,
            term_body='' if term is None else term.body,
            required_permission=required_permission
        )
        return new_space

    def update(self, **kwargs) -> None:
        """
        인자를 전달받아 space instance의 정보를 수정하는 메서드
        그룹 정보의 수정은 지원하지 않는다.
        """
        if 'name' in kwargs.keys():
            self.name = kwargs['name']
        if 'term' in kwargs.keys():
            self.term = kwargs['term']
        if 'required_permission' in kwargs.keys():
            self.required_permission = kwargs['required_permission']

        self.save()


class Reservation(models.Model):
    """
    예약 내역
    - Reservation : Space = N : 1 (한 공간에 여러 예약 내역이 있을 수 있으므로)
    - Reservation : SystemUser = N : 1 (한 사용자가 여러 건의 예약을 할 수 있으므로)
    """
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    space = models.ForeignKey(Space, null=False, on_delete=models.CASCADE,
                              verbose_name='대상 공간', related_name='reservations_as_space')

    member = models.ForeignKey(SystemUser, null=False, on_delete=models.CASCADE,
                               verbose_name='예약자', related_name='reservations_as_member')

    promised_term_body = models.TextField('동의 약관 본문', null=True, blank=True)

    dt_from = models.DateTimeField('예약 시작 일시', blank=False, null=False)
    dt_to = models.DateTimeField('예약 해제 일시', blank=False, null=False)

    class Meta:
        verbose_name = '예약'
        verbose_name_plural = '예약 목록'

    class FindingSingleInstance:
        def init_reservation(self, request, *args, **kwargs):
            target_reservation = get_object_or_404(Reservation, pk=kwargs['reservation_pk'])
            self.reservation = target_reservation
            self.context['reservation'] = self.reservation

    def __str__(self):
        return self.member.username

    @classmethod
    def create_reservation(cls, space: Space, member: SystemUser, target_dt: datetime):
        """
        새 예약 내역을 생성하는 메서드
        :param space: 예약을 생성할 공간
        :param member: 예약자
        :param target_dt: 예약 시작 일시
        :return: 생성된 새 예약 내역
        :raises IntegrityError: 선택된 일시로부터 1시간 간격 안에 예약 내역이 존재하는 경우
        :raises Http404: member check에 실패한 경우
        """
        if cls.already_booked(space, target_dt):
            raise IntegrityError
        else:
            member = space.group.member_check(member)
            new_reservation = cls.objects.create(space=space, member=member,
                                                 promised_term_body='' if space.term is None else space.term.body,
                                                 dt_from=target_dt,
                                                 dt_to=target_dt + timezone.timedelta(minutes=59))
            return new_reservation

    @classmethod
    def already_booked(cls, space: Space, target_dt: datetime) -> bool:
        """
        target_dt로 선택된 일시 기준 1시간 이내에 space에 등록된 예약이 있는지 확인하는 메서드
        :param space: 예약 유무를 검사할 공간
        :param target_dt: 예약 유무를 검사하기 위한 datetime 객체
        :return: 예약이 있으면 True, 없으면 False를 반환
        """
        return cls.objects.filter(space=space, dt_from__gte=target_dt,
                                  dt_to__lt=target_dt + timezone.timedelta(hours=1))

    @classmethod
    def get_reservation_of_week(cls, target_dt: timezone.datetime, space: Space) -> List[Dict[int, 'Reservation']]:
        """
        target_day가 포함된 주의 월요일부터 일요일까지의 예약 내역 중 space에 연결된 reservation instance를
        월요일(reservation_per_weekdays[0])부터 일요일(reservation_per_weekdays[6])까지, 한시간 단위로 모아서 반환하는 메서드
        :param target_dt: 검색할 일주일이 포함하는 날짜
        :param space: Reservation instance를 검색할 space
        :return: 2중첩 리스트(바깥 인덱스: 일주일, 안쪽 인덱스: 0시~23시)
        """
        # target_day의 요일을 구함
        target_weekday = target_dt.weekday()
        # 기준일로부터 월요일, 일요일 날짜를 구함
        monday_start = target_dt - timezone.timedelta(days=target_weekday)
        sunday_end = monday_start + timezone.timedelta(days=7) - timezone.timedelta(seconds=1)

        # 기준일이 포함된 일주일 안에 포함되어 있는 Reservation instance들을 검색
        in_range_reservations = Reservation.objects.filter(space=space, dt_from__gte=monday_start,
                                                           dt_to__lte=sunday_end)

        # 날짜별 reservation instance 정리
        reservation_per_weekdays = []
        for i in range(7):
            # 해당 날짜의 시간대별(1시간 간격) Reservation instance 정리
            tmp = {_h: None for _h in range(24)}

            start = monday_start + timezone.timedelta(days=i)
            end = start + timezone.timedelta(days=1)

            h = start
            while h < end:
                for reservation in in_range_reservations.filter(dt_from__gte=h,
                                                                dt_to__lt=h + timezone.timedelta(hours=1)):
                    tmp[h.hour] = reservation
                h += timezone.timedelta(hours=1)
            reservation_per_weekdays.append(tmp)

        return reservation_per_weekdays

    @staticmethod
    def get_datetime(year, month, day) -> datetime:
        """
        year, month, day를 인자로 전달받아 해당 날짜의 0시 0분 0초로 초기화하여 반환하는 메서드
        인자 중 하나라도 전달되지 않을 경우, 메서드 호출 날짜로 초기화한다.
        """
        if not (year and month and day):
            target_day = timezone.now()
        else:
            try:
                target_day = timezone.datetime(int(year), int(month), int(day))
            except Exception:
                return None

        target_day = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
        return target_day
