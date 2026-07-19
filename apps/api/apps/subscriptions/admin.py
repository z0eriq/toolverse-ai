from django.contrib import admin

from apps.subscriptions.models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "price_cents", "is_active")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end")
    search_fields = ("user__email",)
