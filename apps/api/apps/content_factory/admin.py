from django.contrib import admin

from apps.content_factory.models import (
    AutopilotRun,
    ContentGenerationLog,
    ContentItem,
    ContentVersion,
    PromptTemplate,
)


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "purpose", "locale", "updated_at")
    list_filter = ("purpose", "locale")
    search_fields = ("slug", "name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "content_type", "status", "locale", "published_at")
    list_filter = ("status", "content_type", "locale")
    search_fields = ("title", "slug", "target_path")
    raw_id_fields = ("tool", "created_by")


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    list_display = ("content", "revision", "created_at", "created_by")
    raw_id_fields = ("content", "created_by")


@admin.register(ContentGenerationLog)
class ContentGenerationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "provider", "model", "status", "created_at")
    list_filter = ("status", "provider")
    raw_id_fields = ("content",)


@admin.register(AutopilotRun)
class AutopilotRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "keyword",
        "stage",
        "status",
        "quality_score",
        "is_duplicate",
        "created_at",
    )
    list_filter = ("status", "stage", "is_duplicate")
    raw_id_fields = ("keyword", "content_item")
