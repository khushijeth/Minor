# bellapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest

from .models import Schedule, BellAlert, SystemLog


# =========================
# AUTHENTICATION
# =========================
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not password or not password2:
            return render(request, 'myapp/register.html', {'error': 'Please fill all fields'})

        if password != password2:
            return render(request, 'myapp/register.html', {'error': "Passwords don't match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'myapp/register.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('myapp:dashboard')

    return render(request, 'myapp/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('myapp:dashboard')
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid credentials'})

    return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('myapp:login')


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration')
        date = request.POST.get('date')
        enabled = request.POST.get('enabled') == 'on'

        if name and start_time and duration and date:
            schedule = Schedule.objects.create(
                name=name,
                start_time=start_time,
                duration_minutes=int(duration),
                date=date,
                enabled=enabled
            )

            SystemLog.objects.create(
                action='SCHEDULE_ADD',
                message=f'Schedule "{schedule.name}" added by {request.user.username}'
            )

            return redirect('myapp:dashboard')

    schedules = Schedule.objects.all().order_by('-date', '-start_time')
    return render(request, 'myapp/dashboard.html', {'schedules': schedules})


# =========================
# MANUAL BELL RING
# =========================
@login_required
def manual_ring(request):
    if request.method == 'POST':
        SystemLog.objects.create(
            action='MANUAL_RING',
            message=f'Bell manually rung by {request.user.username}'
        )
        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "Invalid request"}, status=400)


# =========================
# EDIT SCHEDULE
# =========================
@login_required
def edit_schedule(request, schedule_id):
    sched = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration')
        enabled = request.POST.get('enabled') == 'on'

        if name and start_time and duration:
            sched.name = name
            sched.start_time = start_time
            sched.duration_minutes = int(duration)
            sched.enabled = enabled
            sched.save()

            SystemLog.objects.create(
                action='SCHEDULE_EDIT',
                message=f'Schedule "{sched.name}" edited by {request.user.username}'
            )

            return redirect('myapp:dashboard')

    return render(request, 'myapp/edit_schedule.html', {'schedule': sched})


# =========================
# DELETE SCHEDULE
# =========================
@login_required
def delete_schedule(request, schedule_id):
    sched = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        SystemLog.objects.create(
            action='SCHEDULE_DELETE',
            message=f'Schedule "{sched.name}" deleted by {request.user.username}'
        )
        sched.delete()
        return redirect('myapp:dashboard')

    return render(request, 'myapp/delete_schedule_confirm.html', {'schedule': sched})


# =========================
# SYSTEM LOGS PAGE
# =========================
@login_required
def system_logs(request):
    logs = SystemLog.objects.order_by('-timestamp')
    return render(request, 'myapp/logs.html', {'logs': logs})


# =========================
# ALERT FETCH (optional JS)
# =========================
@login_required
def get_alerts(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    pending = BellAlert.objects.filter(shown=False)
    data = []

    for alert in pending:
        data.append({
            "schedule_id": alert.schedule.id,
            "schedule_name": alert.schedule.name,
            "alert_type": alert.alert_type,
            "timestamp": alert.timestamp.isoformat(),
        })

    pending.update(shown=True)
    return JsonResponse({"alerts": data})


# =========================
# STATIC PAGES
# =========================
def about(request):
    return render(request, 'myapp/about.html')


def contact(request):
    return render(request, 'myapp/contact.html')

from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

@csrf_exempt
def api_get_schedules(request):
    """
    ESP32 will call this API
    """
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=400)

    schedules = Schedule.objects.filter(enabled=True)

    data = []
    for s in schedules:
        data.append({
            "id": s.id,
            "name": s.name,
            "date": s.date.strftime("%Y-%m-%d"),
            "start_time": s.start_time.strftime("%H:%M"),
            "duration": s.duration_minutes,
        })

    return JsonResponse({
        "server_time": now().strftime("%Y-%m-%d %H:%M:%S"),
        "schedules": data
    })
