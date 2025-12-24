# myapp/urls.py
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('', views.dashboard, name='dashboard'),
     path('manual-ring/', views.manual_ring, name='manual_ring'),
    
    path('schedule/<int:schedule_id>/edit/', views.edit_schedule, name='edit_schedule'),
    path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),

    path('get-alerts/', views.get_alerts, name='get_alerts'),

     path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('logs/', views.system_logs, name='system_logs'),
    path("api/schedules/", views.api_get_schedules, name="api_schedules"),
]
