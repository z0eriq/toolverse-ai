from rest_framework import serializers

from apps.keywords.models import KeywordOpportunity


class KeywordOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordOpportunity
        fields = (
            "id",
            "keyword",
            "locale",
            "search_volume",
            "difficulty",
            "ranking_position",
            "ctr",
            "clicks",
            "impressions",
            "suggested_tool_slug",
            "priority_score",
            "last_synced_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
