from django.contrib import admin

from apps.seo_optimizer.models import (
    SeoApplyLog,
    SeoAutopilotRun,
    SeoHealthScore,
    SeoOpportunityTask,
    SeoPageIssue,
    SeoRecommendation,
)


@admin.register(SeoRecommendation)
class SeoRecommendationAdmin(admin.ModelAdmin):
    list_display = ("path", "type", "severity", "status", "updated_at")
    list_filter = ("type", "severity", "status")
    search_fields = ("path", "suggestion")


@admin.register(SeoHealthScore)
class SeoHealthScoreAdmin(admin.ModelAdmin):
    list_display = ("path", "overall", "metadata", "schema", "performance", "analyzed_at")
    search_fields = ("path",)
    ordering = ("-overall",)


@admin.register(SeoOpportunityTask)
class SeoOpportunityTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "priority", "status", "suggested_action", "updated_at")
    list_filter = ("source", "status", "suggested_action")
    search_fields = ("title", "path", "rationale")


@admin.register(SeoAutopilotRun)
class SeoAutopilotRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "issues_created", "finished_at", "created_at")
    list_filter = ("status",)


@admin.register(SeoPageIssue)
class SeoPageIssueAdmin(admin.ModelAdmin):
    list_display = ("path", "issue_type", "severity", "status", "created_at")
    list_filter = ("issue_type", "severity", "status")
    search_fields = ("path", "suggestion")


@admin.register(SeoApplyLog)
class SeoApplyLogAdmin(admin.ModelAdmin):
    list_display = ("issue", "applied_by", "created_at")
    search_fields = ("note",)
