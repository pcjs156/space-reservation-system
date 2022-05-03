from django.contrib import admin
from django.urls import path, include

from users import urls as user_urls
from commons import urls as commons_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(commons_urls)),
    path('user/', include(user_urls)),
]
