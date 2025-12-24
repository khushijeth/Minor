from django.contrib import admin
from .models import Schedule, BellAlert, SystemLog

# Register your models here.
admin.site.register(Schedule)
admin.site.register(BellAlert)
admin.site.register(SystemLog)