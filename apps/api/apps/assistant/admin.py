from django.contrib import admin

from apps.assistant.models import AssistantSession


@admin.register(AssistantSession)
class AssistantSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "updated_at")
    raw_id_fields = ("user",)
    search_fields = ("session_key",)
