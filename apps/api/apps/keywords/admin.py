from django.contrib import admin

from apps.keywords.models import KeywordOpportunity


@admin.register(KeywordOpportunity)
class KeywordOpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "keyword",
        "locale",
        "search_volume",
        "difficulty",
        "priority_score",
        "ranking_position",
        "last_synced_at",
    )
    list_filter = ("locale",)
    search_fields = ("keyword", "suggested_tool_slug")
    ordering = ("-priority_score",)
