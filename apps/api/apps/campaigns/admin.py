from django.contrib import admin

from apps.campaigns.models import CampaignResultDaily, MarketingCampaign


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "channel", "status", "budget_cents", "starts_at", "ends_at")
    list_filter = ("status", "channel")
    search_fields = ("key", "name")
    prepopulated_fields = {"key": ("name",)}


@admin.register(CampaignResultDaily)
class CampaignResultDailyAdmin(admin.ModelAdmin):
    list_display = ("campaign", "date", "impressions", "clicks", "conversions", "revenue_cents")
    list_filter = ("date",)
