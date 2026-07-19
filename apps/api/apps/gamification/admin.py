from django.contrib import admin

from apps.gamification.models import Badge, PointsLedger, UserBadge, UserLevel, UserPoints


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "lifetime", "updated_at")
    search_fields = ("user__email",)


@admin.register(PointsLedger)
class PointsLedgerAdmin(admin.ModelAdmin):
    list_display = ("user", "delta", "reason", "balance_after", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__email", "reason", "ref")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "points_required", "is_active")
    list_filter = ("is_active",)
    search_fields = ("slug", "name")


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "created_at")
    search_fields = ("user__email", "badge__slug")


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "title", "updated_at")
    search_fields = ("user__email",)
