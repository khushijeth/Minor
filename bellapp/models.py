from django.db import models
from django.utils import timezone

# class Mode(models.TextChoices):
#     REGULAR = "regular", "Regular Day"
#     EXAM = "exam", "Exam Day"

class Schedule(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()  # or end_time field
    enabled = models.BooleanField(default=True)
    date = models.DateField()
    
    def __str__(self):
        return self.name

class BellAlert(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10)  # e.g. "start" or "end"
    timestamp = models.DateTimeField(default=timezone.now)
    shown = models.BooleanField(default=False)

class SystemLog(models.Model):
    ACTION_CHOICES = [
        ('AUTO_RING', 'Automatic Ring'),
        ('MANUAL_RING', 'Manual Ring'),
        ('SCHEDULE_ADD', 'Schedule Added'),
        ('SCHEDULE_EDIT', 'Schedule Edited'),
        ('SCHEDULE_DELETE', 'Schedule Deleted'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.timestamp}"
