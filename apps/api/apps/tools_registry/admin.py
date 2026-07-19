from django.contrib import admin

from apps.tools_registry.dynamic_models import DynamicToolDefinition
from apps.tools_registry.growth_models import ToolGrowthMeta
from apps.tools_registry.models import Category, Tool


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "order", "is_active", "updated_at")
    search_fields = ("slug",)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("tool_id", "slug", "category", "source", "premium", "is_active", "usage_count")
    list_filter = ("premium", "is_active", "source", "category")
    search_fields = ("tool_id", "slug", "search_document")


@admin.register(DynamicToolDefinition)
class DynamicToolDefinitionAdmin(admin.ModelAdmin):
    list_display = ("slug", "category_slug", "status", "premium", "revision", "updated_at")
    list_filter = ("status", "premium", "category_slug")
    search_fields = ("slug",)


@admin.register(ToolGrowthMeta)
class ToolGrowthMetaAdmin(admin.ModelAdmin):
    list_display = ("tool", "is_viral", "og_template", "updated_at")
    list_filter = ("is_viral",)
    search_fields = ("tool__slug", "tool__tool_id")
