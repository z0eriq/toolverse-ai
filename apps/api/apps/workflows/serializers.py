from __future__ import annotations

from rest_framework import serializers

from apps.workflows.models import Workflow, WorkflowRun, WorkflowTemplate, WorkflowUsageDaily


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplate
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "steps",
            "category",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = (
            "id",
            "name",
            "slug",
            "steps",
            "visibility",
            "share_token",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "share_token", "created_at", "updated_at")


class WorkflowRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowRun
        fields = (
            "id",
            "workflow",
            "status",
            "input",
            "output",
            "error",
            "duration_ms",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkflowUsageDailySerializer(serializers.ModelSerializer):
    workflow_slug = serializers.CharField(source="workflow.slug", read_only=True)

    class Meta:
        model = WorkflowUsageDaily
        fields = ("id", "workflow", "workflow_slug", "date", "runs")
        read_only_fields = fields
