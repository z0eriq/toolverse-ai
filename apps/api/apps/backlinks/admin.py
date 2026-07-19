from django.contrib import admin

from apps.backlinks.models import (
    BacklinkCampaign,
    BacklinkOpportunity,
    BacklinkOutreachLog,
    BacklinkTarget,
)


@admin.register(BacklinkTarget)
class BacklinkTargetAdmin(admin.ModelAdmin):
    list_display = ("title", "path", "url", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "url", "path")


@admin.register(BacklinkCampaign)
class BacklinkCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "target", "status", "updated_at")
    list_filter = ("status",)


@admin.register(BacklinkOpportunity)
class BacklinkOpportunityAdmin(admin.ModelAdmin):
    list_display = ("source_domain", "target", "priority", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("source_domain", "source_url")


@admin.register(BacklinkOutreachLog)
class BacklinkOutreachLogAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "channel", "outcome", "created_at")
    list_filter = ("channel",)
