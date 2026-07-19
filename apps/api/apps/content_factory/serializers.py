from rest_framework import serializers

from apps.content_factory.models import AutopilotRun, ContentItem, ContentVersion, PromptTemplate


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = (
            "id",
            "slug",
            "name",
            "template_text",
            "purpose",
            "locale",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ContentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVersion
        fields = ("id", "revision", "body", "meta_snapshot", "created_at", "created_by")
        read_only_fields = fields


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = (
            "id",
            "title",
            "slug",
            "body",
            "content_type",
            "status",
            "locale",
            "tool",
            "target_path",
            "meta_title",
            "meta_description",
            "created_by",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "published_at", "created_at", "updated_at")


class ContentGenerateSerializer(serializers.Serializer):
    template_slug = serializers.SlugField()
    variables = serializers.DictField(required=False, default=dict)
    provider = serializers.CharField(required=False, allow_blank=True, default="")
    model = serializers.CharField(required=False, allow_blank=True, default="")


class AutopilotRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutopilotRun
        fields = (
            "id",
            "keyword",
            "stage",
            "status",
            "content_item",
            "quality_score",
            "is_duplicate",
            "error",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AutopilotRunCreateSerializer(serializers.Serializer):
    keyword_id = serializers.IntegerField()
    async_mode = serializers.BooleanField(required=False, default=False)
