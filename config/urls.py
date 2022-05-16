from django.contrib import admin
from django.urls import path, include

from users import urls as user_urls
from commons import urls as commons_urls
from reservations import urls as reservation_urls

from commons import views as common_views

handler404 = common_views.handler_404_view
handler500 = common_views.handler_500_view

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    # Include common app
    path('', include(commons_urls)),
    # Include users app
    path('user/', include(user_urls)),
    # Include reservation app
    path('reservation/', include(reservation_urls)),
]
