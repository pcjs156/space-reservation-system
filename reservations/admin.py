from django.contrib import admin

from .models import Term, Space, Reservation

admin.site.register(Term)
admin.site.register(Space)
admin.site.register(Reservation)
