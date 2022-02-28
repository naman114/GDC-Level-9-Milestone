from django.db import models

from django.contrib.auth.models import User

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )

    def __str__(self):
        return self.title


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    previous_status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    current_status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.task)


class EmailPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    selected_email_hour = models.IntegerField(default=0)
    previous_report_day = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)
