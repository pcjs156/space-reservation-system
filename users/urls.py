from django.urls import path, include
from . import views

app_name = 'users'

group_urlpatterns = [
    # 그룹 목록
    path('', views.group_list_view, name='group'),
    # 그룹 멤버 상세 정보
    path('<int:group_pk>/<int:member_pk>/', views.group_member_detail_view, name='group_member_detail'),
    # 그룹 탈퇴
    path('<int:group_pk>/<int:member_pk>/withdraw/', views.group_withdraw_view, name='group_member_withdraw'),

    # 그룹 매니저 사용 ===================================================================================================
    # 그룹 정보 관리 화면
    path('<int:group_pk>/manage/', views.group_manage_view, name='group_manage'),
    # 그룹 상세 정보
    path('<int:group_pk>/', views.group_detail_view, name='group_detail'),
    # 그룹 삭제
    path('<int:group_pk>/manage/delete/', views.group_delete_view, name='group_delete'),

    # 그룹 사용 제한/권한 -------------------------------------------------------------------------------------------------
    # 사용 제한
    path('<int:group_pk>/manage/<int:member_pk>/block/', views.block_list_view,
         name='group_member_block'),
    # 사용 제한 해제
    path('<int:group_pk>/manage/<int:member_pk>/block/<int:block_pk>/delete/', views.block_delete_view,
         name='delete_group_member_block'),
    path('<int:group_pk>/manage/<int:member_pk>/kick/', views.kick_group_member_view, name='group_member_kick'),
    # 권한 관리
    path('<int:group_pk>/manage/<int:member_pk>/permission/', views.group_member_permission_view,
         name='group_member_permission'),
    # 매니저 권한 위임
    path('<int:group_pk>/manage/<int:member_pk>/handover/', views.group_manager_handover_view,
         name='group_manager_handover'),

    # 그룹 가입 ---------------------------------------------------------------------------------------------------------
    # 그룹 검색
    path('search/', views.group_search_view, name='group_search'),
    # 그룹 검색 결과
    path(r'^search/(?P<str:invite_code>\w+))/$', views.group_search_view, name='group_search'),
    # 그룹 초대 코드 변경
    path('<int:group_pk>/manage/reissue-intie-code/', views.group_invite_code_change_view,
         name='group_reissue_invite_code'),
    # 그룹 가입 요청
    path('join/', views.group_join_request, name='group_join_request'),
    # 그룹 가입 요청 승인
    path('<int:group_pk>/manage/<int:user_pk>/join/<int:request_pk>/accept/', views.accept_join_request_view,
         name='group_join_accept'),
    # 그룹 가입 요청 거절
    path('<int:group_pk>/manage/<int:user_pk>/join/<int:request_pk>/reject/', views.reject_join_request_view,
         name='group_join_reject'),
]

urlpatterns = [
    # 로그인
    path('login/', views.login_view, name='login'),
    # 로그아웃
    path('logout/', views.logout_view, name='logout'),
    # 회원가입
    path('sign-up/', views.signup_view, name='sign_up'),
    # 로그인한 사용자에 대한 로그아웃 요청
    path('request-logout/', views.request_logout_view, name='request_logout'),
    # 계정 정보 수정
    path('info/', views.modify_info_view, name='modify_account_info'),
    # 그룹 관련
    path('group/', include(group_urlpatterns)),
]
