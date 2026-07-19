from __future__ import annotations

from rest_framework import serializers

from apps.creator_hub.models import (
    CreatorProfile,
    CreatorRevenueShareStub,
    CreatorSubmission,
    CreatorUsageStat,
)


class CreatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorProfile
        fields = (
            "id",
            "display_name",
            "bio",
            "payout_ready",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "payout_ready", "created_at", "updated_at")


class CreatorSubmissionSerializer(serializers.ModelSerializer):
    tool_spec_slug = serializers.CharField(
        source="tool_spec.slug", read_only=True, allow_null=True
    )

    class Meta:
        model = CreatorSubmission
        fields = (
            "id",
            "type",
            "payload",
            "tool_spec",
            "tool_spec_slug",
            "status",
            "reviewer_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "tool_spec",
            "tool_spec_slug",
            "status",
            "reviewer_notes",
            "created_at",
            "updated_at",
        )


class CreatorUsageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorUsageStat
        fields = ("id", "submission", "tool_slug", "period", "runs", "unique_users")
        read_only_fields = fields


class CreatorRevenueShareStubSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorRevenueShareStub
        fields = (
            "id",
            "period",
            "amount_cents",
            "share_bps",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
