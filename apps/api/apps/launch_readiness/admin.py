from django.contrib import admin

from apps.launch_readiness.models import ReadinessCheck


@admin.register(ReadinessCheck)
class ReadinessCheckAdmin(admin.ModelAdmin):
    list_display = ("key", "category", "status", "checked_at", "updated_at")
    list_filter = ("category", "status")
    search_fields = ("key", "detail")
