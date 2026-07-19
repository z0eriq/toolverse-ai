from django.contrib import admin

from apps.jobs.models import AsyncJob


@admin.register(AsyncJob)
class AsyncJobAdmin(admin.ModelAdmin):
    list_display = ("id", "tool_id", "status", "user", "progress", "created_at")
    list_filter = ("status",)
    search_fields = ("tool_id", "user__email")
