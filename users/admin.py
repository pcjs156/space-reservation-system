from django.contrib import admin
from django.contrib.auth.models import Group as default_django_group

from .models import SystemUser, Group, PermissionTag, Block, JoinRequest

admin.site.unregister(default_django_group)

admin.site.register(SystemUser)
admin.site.register(Group)
admin.site.register(PermissionTag)
admin.site.register(Block)
admin.site.register(JoinRequest)
