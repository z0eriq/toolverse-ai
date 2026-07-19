from django.contrib import admin

from apps.ai_providers.models import AIUsageLog


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "model", "user", "tool_id", "tokens_in", "tokens_out", "created_at")
    list_filter = ("provider",)
    search_fields = ("model", "tool_id", "user__email")
