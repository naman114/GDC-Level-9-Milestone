from django.core.mail import send_mail
from tasks.models import EmailPreferences, Task, STATUS_CHOICES
from datetime import datetime

from celery.schedules import crontab

from task_manager.celery import app


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Setup an hourly job to check all users' email preferences and send out reports for those due
    sender.add_periodic_task(crontab(hour="*", minute=0), check_email_preferences.s())


@app.task
def check_email_preferences():
    current_date = datetime.now().day
    current_hour = datetime.now().hour

    reports_to_send = EmailPreferences.objects.filter(
        selected_email_hour__lte=current_hour
    ).exclude(previous_report_day=current_date)

    for email_preference in reports_to_send:
        send_email_reminder(email_preference.user)
        email_preference.previous_report_day = current_date
        email_preference.save()


def send_email_reminder(user):
    print(f"Starting to send email to user {user}")

    email_content = "Task Manager Report\n"

    for status_choice in STATUS_CHOICES:
        tasks_count = Task.objects.filter(
            user=user, deleted=False, status=status_choice[0]
        ).count()
        email_content += f"{status_choice[0]} tasks: {tasks_count}\n"

    send_mail(
        "Daily Report from Task Manager",
        email_content,
        "tasks@task_manager.org",
        [user.email],
    )

    print(f"Email sent to user {user}")
