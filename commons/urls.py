from django.urls import path

from . import views

app_name = 'commons'

urlpatterns = [
    # 메인 화면
    path('', views.main_view, name='main'),
]
