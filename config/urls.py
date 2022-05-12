from django.contrib import admin
from django.urls import path, include

from users import urls as user_urls
from commons import urls as commons_urls
from reservations import urls as reservation_urls

from commons import views as common_views

handler404 = common_views.handler_404_view
handler500 = common_views.handler_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(commons_urls)),
    path('user/', include(user_urls)),
    path('reservation/', include(reservation_urls)),
]
