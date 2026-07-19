from __future__ import annotations

from rest_framework import serializers

from apps.competitor_intel.models import CompetitorDomain, CompetitorOpportunity


class CompetitorDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorDomain
        fields = (
            "id",
            "domain",
            "name",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CompetitorOpportunitySerializer(serializers.ModelSerializer):
    competitor_domain = serializers.CharField(source="competitor.domain", read_only=True)

    class Meta:
        model = CompetitorOpportunity
        fields = (
            "id",
            "competitor",
            "competitor_domain",
            "keyword",
            "title",
            "rationale",
            "gap_score",
            "status",
            "evidence",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
