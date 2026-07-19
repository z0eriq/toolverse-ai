from django.contrib import admin

from apps.history.models import ToolHistory


@admin.register(ToolHistory)
class ToolHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "tool", "action", "created_at")
    search_fields = ("user__email", "tool__tool_id")
