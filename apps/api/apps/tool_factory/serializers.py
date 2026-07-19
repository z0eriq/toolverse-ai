from __future__ import annotations

from rest_framework import serializers

from apps.tool_factory.models import ToolFactoryJob, ToolSpec


class ToolSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolSpec
        fields = (
            "id",
            "slug",
            "category_slug",
            "name",
            "description",
            "ui_schema",
            "pipeline",
            "seo",
            "faq",
            "howto",
            "capabilities",
            "recipe",
            "status",
            "error",
            "is_viral",
            "share_text",
            "export_filesystem",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "error", "created_by", "created_at", "updated_at")


class ToolFactoryJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolFactoryJob
        fields = (
            "id",
            "spec",
            "celery_task_id",
            "status",
            "log",
            "artifacts",
            "created_at",
        )
        read_only_fields = fields
