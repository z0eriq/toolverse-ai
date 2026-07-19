from __future__ import annotations

from rest_framework import serializers

from apps.growth_agent.models import GrowthAction, GrowthAgentRun, GrowthInsight, GrowthTask


class GrowthInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthInsight
        fields = (
            "id",
            "category",
            "title",
            "rationale",
            "priority",
            "status",
            "meta",
            "source_snapshot",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class GrowthAgentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthAgentRun
        fields = (
            "id",
            "status",
            "summary",
            "insights_created",
            "error",
            "finished_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class GrowthTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthTask
        fields = (
            "id",
            "title",
            "category",
            "priority",
            "status",
            "insight",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class GrowthActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthAction
        fields = (
            "id",
            "task",
            "action_type",
            "payload",
            "status",
            "result_ref",
            "error",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
