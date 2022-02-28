from django.contrib import admin

# Register your models here.

from tasks.models import Task, TaskHistory, EmailPreferences

admin.sites.site.register(Task)


class TaskHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at",)


admin.sites.site.register(TaskHistory, TaskHistoryAdmin)

admin.sites.site.register(EmailPreferences)
