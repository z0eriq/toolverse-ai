from django.contrib import admin

from apps.recommendations.models import ToolAffinity, ToolRelationship


@admin.register(ToolAffinity)
class ToolAffinityAdmin(admin.ModelAdmin):
    list_display = ("tool_a", "tool_b", "score", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("tool_a__slug", "tool_b__slug", "tool_a__tool_id", "tool_b__tool_id")
    raw_id_fields = ("tool_a", "tool_b")
    ordering = ("-score",)


@admin.register(ToolRelationship)
class ToolRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        "source_tool",
        "target_tool",
        "relationship_score",
        "reason",
        "updated_at",
    )
    list_filter = ("reason",)
    search_fields = (
        "source_tool__slug",
        "target_tool__slug",
        "source_tool__tool_id",
        "target_tool__tool_id",
    )
    raw_id_fields = ("source_tool", "target_tool")
    ordering = ("-relationship_score",)
