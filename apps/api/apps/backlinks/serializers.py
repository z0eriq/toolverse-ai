from __future__ import annotations

from rest_framework import serializers

from apps.backlinks.models import (
    BacklinkCampaign,
    BacklinkOpportunity,
    BacklinkOutreachLog,
    BacklinkTarget,
)


class BacklinkTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacklinkTarget
        fields = (
            "id",
            "url",
            "path",
            "title",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class BacklinkCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacklinkCampaign
        fields = (
            "id",
            "name",
            "target",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class BacklinkOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BacklinkOpportunity
        fields = (
            "id",
            "campaign",
            "target",
            "source_domain",
            "source_url",
            "contact_email",
            "priority",
            "status",
            "rationale",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class BacklinkOutreachLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacklinkOutreachLog
        fields = (
            "id",
            "opportunity",
            "channel",
            "message",
            "outcome",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
