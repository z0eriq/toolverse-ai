from django.contrib import admin

from apps.workflows.models import Workflow, WorkflowRun, WorkflowTemplate, WorkflowUsageDaily


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "category", "is_public", "updated_at")
    list_filter = ("category", "is_public")
    search_fields = ("slug", "name")


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "visibility", "updated_at")
    list_filter = ("visibility",)
    search_fields = ("name", "slug", "owner__email")


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "status", "duration_ms", "created_at")
    list_filter = ("status",)


@admin.register(WorkflowUsageDaily)
class WorkflowUsageDailyAdmin(admin.ModelAdmin):
    list_display = ("workflow", "date", "runs")
