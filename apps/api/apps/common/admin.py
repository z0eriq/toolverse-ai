from django.contrib import admin

from apps.common.models import AuditLog, BlockedIP, PushSubscription


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "resource_type", "resource_id", "actor", "ip", "created_at")
    list_filter = ("action", "resource_type")
    search_fields = ("action", "resource_type", "resource_id", "ip")
    raw_id_fields = ("actor",)
    readonly_fields = (
        "actor",
        "action",
        "resource_type",
        "resource_id",
        "ip",
        "user_agent",
        "meta",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ("ip", "is_active", "reason", "expires_at", "created_at")
    list_filter = ("is_active",)
    search_fields = ("ip", "reason")


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "endpoint", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("endpoint", "user__email")
    raw_id_fields = ("user",)
