from rest_framework import serializers

from apps.campaigns.models import CampaignResultDaily, MarketingCampaign


class MarketingCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingCampaign
        fields = (
            "id",
            "key",
            "name",
            "channel",
            "status",
            "budget_cents",
            "starts_at",
            "ends_at",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CampaignResultDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignResultDaily
        fields = (
            "id",
            "campaign",
            "date",
            "impressions",
            "clicks",
            "conversions",
            "revenue_cents",
        )
        read_only_fields = ("id",)
