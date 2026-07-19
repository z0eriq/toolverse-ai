from __future__ import annotations

from rest_framework import serializers

from apps.monetization.models import (
    AdOptimizationRec,
    AdPerformanceDaily,
    AdPlacement,
    AffiliateLink,
    RevenueEvent,
    SponsoredTool,
)


class AdPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPlacement
        fields = ("id", "key", "enabled", "network", "config", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SponsoredToolSerializer(serializers.ModelSerializer):
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)

    class Meta:
        model = SponsoredTool
        fields = (
            "id",
            "tool",
            "tool_slug",
            "sponsor_name",
            "start_at",
            "end_at",
            "priority",
            "creative",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "tool_slug", "created_at", "updated_at")


class AffiliateLinkSerializer(serializers.ModelSerializer):
    tool_slug = serializers.CharField(source="tool.slug", read_only=True, allow_null=True)

    class Meta:
        model = AffiliateLink
        fields = (
            "id",
            "tool",
            "tool_slug",
            "label",
            "destination_url",
            "network",
            "utm",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "tool_slug", "created_at", "updated_at")


class RevenueEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueEvent
        fields = ("id", "type", "amount_cents", "currency", "meta", "created_at")
        read_only_fields = ("id", "created_at")


class AdPerformanceDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPerformanceDaily
        fields = (
            "id",
            "date",
            "placement_key",
            "impressions",
            "clicks",
            "revenue_cents",
            "ctr",
            "rpm",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AdOptimizationRecSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdOptimizationRec
        fields = (
            "id",
            "placement_key",
            "title",
            "rationale",
            "priority",
            "status",
            "evidence",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
