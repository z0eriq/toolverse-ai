from django.contrib import admin

from apps.analytics.models import AnalyticsDailyRollup, AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tool_id",
        "utm_source",
        "campaign_key",
        "country",
        "user",
        "path",
        "created_at",
    )
    list_filter = ("name", "country", "utm_source", "created_at")
    search_fields = ("name", "path", "tool_id", "session_id", "campaign_key", "utm_campaign")


@admin.register(AnalyticsDailyRollup)
class AnalyticsDailyRollupAdmin(admin.ModelAdmin):
    list_display = ("date", "event_name", "tool_id", "country", "count")
    list_filter = ("date", "event_name", "country")
    search_fields = ("tool_id", "event_name")
