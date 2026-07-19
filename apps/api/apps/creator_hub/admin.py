from django.contrib import admin

from apps.creator_hub.models import (
    CreatorProfile,
    CreatorRevenueShareStub,
    CreatorSubmission,
    CreatorUsageStat,
)


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "payout_ready", "updated_at")
    search_fields = ("display_name", "user__email")


@admin.register(CreatorSubmission)
class CreatorSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "status", "creator", "tool_spec", "updated_at")
    list_filter = ("type", "status")


@admin.register(CreatorUsageStat)
class CreatorUsageStatAdmin(admin.ModelAdmin):
    list_display = ("tool_slug", "period", "runs", "unique_users")


@admin.register(CreatorRevenueShareStub)
class CreatorRevenueShareStubAdmin(admin.ModelAdmin):
    list_display = ("creator", "period", "amount_cents", "share_bps", "status")
    list_filter = ("status",)
