from django.contrib import admin

from apps.programmatic_seo.models import ProgrammaticPage


@admin.register(ProgrammaticPage)
class ProgrammaticPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "page_type", "status", "category_slug", "topic", "updated_at")
    list_filter = ("status", "page_type", "category_slug")
    search_fields = ("slug", "keyword", "topic", "audience")
