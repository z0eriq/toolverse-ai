from django.contrib import admin

from apps.engagement.models import (
    Collection,
    CollectionItem,
    SavedOutput,
    ToolComment,
    ToolReview,
)


@admin.register(SavedOutput)
class SavedOutputAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "tool", "created_at")
    raw_id_fields = ("user", "tool")
    search_fields = ("title",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "user", "updated_at")
    raw_id_fields = ("user",)
    search_fields = ("name", "slug")


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ("collection", "tool", "order")
    raw_id_fields = ("collection", "tool")


@admin.register(ToolReview)
class ToolReviewAdmin(admin.ModelAdmin):
    list_display = ("tool", "user", "rating", "status", "created_at")
    list_filter = ("status", "rating")
    raw_id_fields = ("user", "tool")


@admin.register(ToolComment)
class ToolCommentAdmin(admin.ModelAdmin):
    list_display = ("tool", "user", "status", "created_at")
    list_filter = ("status",)
    raw_id_fields = ("user", "tool", "parent")
