from django.contrib import admin

from apps.search_console.models import GSCMetricSnapshot, GSCProperty, IndexedUrl


@admin.register(GSCProperty)
class GSCPropertyAdmin(admin.ModelAdmin):
    list_display = ("site_url", "is_active", "credentials_ref", "updated_at")
    list_filter = ("is_active",)


@admin.register(GSCMetricSnapshot)
class GSCMetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "query", "page", "clicks", "impressions", "ctr", "position")
    list_filter = ("date", "device", "country")
    search_fields = ("query", "page")


@admin.register(IndexedUrl)
class IndexedUrlAdmin(admin.ModelAdmin):
    list_display = (
        "url_path",
        "status",
        "impressions",
        "clicks",
        "position",
        "ranking_delta",
        "last_crawled_at",
    )
    list_filter = ("status",)
    search_fields = ("url_path",)
