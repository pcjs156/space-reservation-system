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
    path('group/<int:pk>/', views.group_detail_view, name='group_detail'),
]
