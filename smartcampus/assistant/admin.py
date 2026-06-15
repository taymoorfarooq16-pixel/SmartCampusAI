from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FAQ, Event, Timetable

admin.site.register(FAQ)
admin.site.register(Event)
admin.site.register(Timetable)
from django.contrib import admin
from .models import LostItem

admin.site.register(LostItem)
from .models import Attendance

admin.site.register(Attendance)