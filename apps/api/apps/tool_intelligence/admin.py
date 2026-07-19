from django.contrib import admin

from apps.tool_intelligence.models import ToolOpportunity, ToolPerformanceScore, ToolTemplate


@admin.register(ToolTemplate)
class ToolTemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "category_slug", "recipe", "priority_weight")
    list_filter = ("category_slug", "recipe")
    search_fields = ("slug", "description")


@admin.register(ToolOpportunity)
class ToolOpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "suggested_slug",
        "category_slug",
        "priority_score",
        "status",
        "seo_score",
        "demand_score",
    )
    list_filter = ("status", "category_slug")
    search_fields = ("suggested_slug", "title")
    filter_horizontal = ("keywords",)


@admin.register(ToolPerformanceScore)
class ToolPerformanceScoreAdmin(admin.ModelAdmin):
    list_display = (
        "tool",
        "priority_score",
        "traffic_score",
        "usage_score",
        "seo_score",
        "computed_at",
    )
    search_fields = ("tool__tool_id", "tool__slug")
