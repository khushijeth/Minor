# project_name/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bellapp.urls', namespace='bellapp')),
    # … any other URLs …
]
