from rest_framework import serializers

from apps.tool_intelligence.models import (
    ToolOpportunity,
    ToolPerformanceScore,
    ToolTemplate,
)


class ToolTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolTemplate
        fields = (
            "id",
            "slug",
            "category_slug",
            "recipe",
            "ui_schema",
            "pipeline",
            "priority_weight",
            "description",
            "created_at",
            "updated_at",
        )


class ToolOpportunitySerializer(serializers.ModelSerializer):
    keyword_ids = serializers.PrimaryKeyRelatedField(
        source="keywords",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ToolOpportunity
        fields = (
            "id",
            "suggested_slug",
            "category_slug",
            "title",
            "rationale",
            "seo_score",
            "demand_score",
            "competition_score",
            "value_score",
            "priority_score",
            "status",
            "keyword_ids",
            "tool_spec",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ToolPerformanceScoreSerializer(serializers.ModelSerializer):
    tool_id = serializers.CharField(source="tool.tool_id", read_only=True)
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)

    class Meta:
        model = ToolPerformanceScore
        fields = (
            "id",
            "tool",
            "tool_id",
            "tool_slug",
            "traffic_score",
            "usage_score",
            "revenue_score",
            "seo_score",
            "retention_score",
            "priority_score",
            "computed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
