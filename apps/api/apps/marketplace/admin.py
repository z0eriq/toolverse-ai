from django.contrib import admin

from apps.marketplace.models import (
    ApiInvoiceStub,
    ApiKey,
    ApiUsage,
    DeveloperOrganization,
    SalesLead,
)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "key_prefix",
        "usage_this_month",
        "monthly_quota",
        "revoked_at",
        "last_used_at",
        "created_at",
    )
    list_filter = ("revoked_at", "created_at")
    search_fields = ("name", "key_prefix", "user__email")
    readonly_fields = ("key_prefix", "key_hash", "usage_this_month", "last_used_at", "created_at")
    raw_id_fields = ("user",)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["api_key_metrics"] = {
            "total": ApiKey.objects.count(),
            "active": ApiKey.objects.filter(revoked_at__isnull=True).count(),
            "revoked": ApiKey.objects.filter(revoked_at__isnull=False).count(),
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ApiUsage)
class ApiUsageAdmin(admin.ModelAdmin):
    list_display = ("api_key", "endpoint", "method", "status_code", "units", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("endpoint", "api_key__key_prefix", "api_key__name")
    raw_id_fields = ("api_key",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(DeveloperOrganization)
class DeveloperOrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "plan_tier", "created_at")
    list_filter = ("plan_tier",)
    search_fields = ("name", "owner__email")
    raw_id_fields = ("owner",)


@admin.register(ApiInvoiceStub)
class ApiInvoiceStubAdmin(admin.ModelAdmin):
    list_display = (
        "org",
        "period_start",
        "period_end",
        "amount_cents",
        "usage_units",
        "status",
    )
    list_filter = ("status",)
    raw_id_fields = ("org",)


@admin.register(SalesLead)
class SalesLeadAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "company", "intent", "status", "created_at")
    list_filter = ("intent", "status")
    search_fields = ("email", "name", "company")
