from django.contrib import admin

from apps.tool_factory.models import ToolFactoryJob, ToolSpec


@admin.register(ToolSpec)
class ToolSpecAdmin(admin.ModelAdmin):
    list_display = ("slug", "category_slug", "recipe", "status", "is_viral", "updated_at")
    list_filter = ("status", "recipe", "category_slug", "is_viral")
    search_fields = ("slug",)


@admin.register(ToolFactoryJob)
class ToolFactoryJobAdmin(admin.ModelAdmin):
    list_display = ("id", "spec", "status", "celery_task_id", "created_at")
    list_filter = ("status",)
    search_fields = ("spec__slug", "celery_task_id")
