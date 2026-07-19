from django.contrib import admin

from apps.blog.models import BlogPost, BlogTag


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "author")
    list_filter = ("status",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
