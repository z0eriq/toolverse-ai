from django.contrib import admin

from apps.monetization.models import (
    AdOptimizationRec,
    AdPerformanceDaily,
    AdPlacement,
    AffiliateLink,
    RevenueEvent,
    SponsoredTool,
)


@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled", "network", "updated_at")
    list_filter = ("enabled", "network")


@admin.register(SponsoredTool)
class SponsoredToolAdmin(admin.ModelAdmin):
    list_display = ("sponsor_name", "tool", "priority", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("sponsor_name", "tool__slug")


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "tool", "network", "is_active", "updated_at")
    list_filter = ("is_active", "network")
    search_fields = ("label", "destination_url")


@admin.register(RevenueEvent)
class RevenueEventAdmin(admin.ModelAdmin):
    list_display = ("type", "amount_cents", "currency", "created_at")
    list_filter = ("type", "currency")


@admin.register(AdPerformanceDaily)
class AdPerformanceDailyAdmin(admin.ModelAdmin):
    list_display = ("date", "placement_key", "impressions", "clicks", "revenue_cents", "ctr")
    list_filter = ("placement_key",)


@admin.register(AdOptimizationRec)
class AdOptimizationRecAdmin(admin.ModelAdmin):
    list_display = ("title", "placement_key", "priority", "status", "created_at")
    list_filter = ("status", "placement_key")
    search_fields = ("title", "rationale")
