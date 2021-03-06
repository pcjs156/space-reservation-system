from django.urls import path, include

from . import views

app_name = 'reservations'

terms_urlpatterns = [
    # 그룹 내 약관 목록
    path('<int:group_pk>/', views.TermListView.as_view(), name='term_list'),
    # 약관 등록
    path('<int:group_pk>/create/', views.TermCreateView.as_view(), name='term_create'),
    # 약관 삭제
    path('<int:group_pk>/delete/<int:term_pk>/', views.TermDeleteView.as_view(), name='term_delete'),
    # 약관 수정
    path('<int:group_pk>/update/<int:term_pk>/', views.TermUpdateView.as_view(), name='term_update'),
]

spaces_urlpatterns = [
    # 그룹 내 공간 목록
    path('<int:group_pk>/', views.SpaceListView.as_view(), name='space_list'),
    # 공간 상세 정보 (공간 메인 페이지)
    path('<int:group_pk>/<int:space_pk>/', views.SpaceDetailView.as_view(), name='space_detail'),
    # 공간 등록
    path('<int:group_pk>/create/', views.SpaceCreateView.as_view(), name='space_create'),
    # 공간 정보 갱신
    path('<int:group_pk>/<int:space_pk>/update/', views.SpaceUpdateView.as_view(), name='space_update'),
    # 공간 삭제
    path('<int:group_pk>/<int:space_pk>/delete/', views.SpaceDeleteView.as_view(), name='space_delete'),

    # 예약 생성
    path('<int:group_pk>/<int:space_pk>/reservation/create/',
         views.CreateReservationView.as_view(), name='reservation_create'),
    # 예약 상세
    path('<int:group_pk>/<int:space_pk>/reservation/<int:reservation_pk>/',
         views.ReservationDetailView.as_view(), name='reservation_detail'),
    # 예약 삭제
    path('<int:group_pk>/<int:space_pk>/reservation/<int:reservation_pk>/delete',
         views.ReservationDeleteView.as_view(), name='reservation_delete'),
]

urlpatterns = [
    # 약관 관련
    path('terms/', include(terms_urlpatterns)),
    # 공간 관련
    path('spaces/', include(spaces_urlpatterns)),
]
