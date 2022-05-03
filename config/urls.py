from django.contrib import admin
from django.urls import path, include

from users import urls as user_urls
from config import common_views

app_name = 'config'

common_urlpatterns = [
    path('', common_views.main_view),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(user_urls)),
]

urlpatterns += common_urlpatterns
