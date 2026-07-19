from django.contrib import admin

from apps.referrals.models import (
    ReferralAttribution,
    ReferralCode,
    ReferralEvent,
    ReferralReward,
)


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "is_active", "created_at")
    search_fields = ("code", "user__email")


@admin.register(ReferralAttribution)
class ReferralAttributionAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referee", "status", "ip", "created_at")
    list_filter = ("status",)
    search_fields = ("referrer__email", "referee__email")


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount", "status", "created_at")
    list_filter = ("type", "status")


@admin.register(ReferralEvent)
class ReferralEventAdmin(admin.ModelAdmin):
    list_display = ("kind", "code", "user", "ip", "created_at")
    list_filter = ("kind",)
