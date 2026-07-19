from rest_framework import serializers

from apps.subscriptions.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "slug",
            "name",
            "description",
            "price_cents",
            "currency",
            "features",
            "monthly_tool_runs",
            "api_monthly_quota",
            "ads_free",
            "history_days",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "plan",
            "status",
            "is_active",
            "current_period_end",
            "created_at",
        )
