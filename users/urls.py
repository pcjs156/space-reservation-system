from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('request-logout/', views.request_logout_view, name='request_logout'),
    path('sign-up/', views.signup_view, name='sign_up'),
    path('info/', views.modify_info_view, name='modify_account_info'),
    path('group/', views.group_list_view, name='group'),
    path('group/<int:group_pk>/', views.group_detail_view, name='group_detail'),
    path('group/<int:group_pk>/manage/', views.group_manage_view, name='group_manage'),
    path('group/<int:group_pk>/manage/delete/', views.group_delete_view, name='group_delete'),
    path('group/<int:group_pk>/manage/reissue-intie-code/', views.group_invite_code_change_view,
         name='group_reissue_invite_code'),
    path('group/search/', views.group_search_view, name='group_search'),
    path(r'^group/search/(?P<str:invite_code>\w+))/$', views.group_search_view, name='group_search'),
    path('group/join/', views.group_join_request, name='group_join_request'),
    path('group/<int:group_pk>/<int:member_pk>/', views.group_member_detail_view, name='group_member_detail'),
    path('group/<int:group_pk>/<int:member_pk>/withdraw/', views.group_withdraw_view, name='group_member_withdraw'),
]
