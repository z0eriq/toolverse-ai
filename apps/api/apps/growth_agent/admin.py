from django.contrib import admin

from apps.growth_agent.models import GrowthAction, GrowthAgentRun, GrowthInsight, GrowthTask


@admin.register(GrowthInsight)
class GrowthInsightAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "status", "created_at")
    list_filter = ("category", "status")
    search_fields = ("title", "rationale")


@admin.register(GrowthAgentRun)
class GrowthAgentRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "insights_created", "finished_at", "created_at")
    list_filter = ("status",)


@admin.register(GrowthTask)
class GrowthTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "status", "insight", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title",)


@admin.register(GrowthAction)
class GrowthActionAdmin(admin.ModelAdmin):
    list_display = ("id", "action_type", "status", "task", "created_at")
    list_filter = ("action_type", "status")
    search_fields = ("error",)
