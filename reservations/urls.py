from django.urls import path

from . import views

app_name = 'reservations'

urlpatterns = [
    path('terms/<int:group_pk>/', views.term_list_view, name='term_list'),
    path('terms/<int:group_pk>/create/', views.term_create_view, name='term_create'),
    path('terms/<int:group_pk>/delete/<int:term_pk>/', views.term_delete_view, name='term_delete'),
    path('terms/<int:group_pk>/update/<int:term_pk>/', views.term_update_view, name='term_update'),
    path('spaces/<int:group_pk>/', views.space_list_view, name='space_list'),
    path('spaces/<int:group_pk>/create/', views.space_create_view, name='space_create'),
]
