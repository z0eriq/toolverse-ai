from rest_framework import serializers

from apps.tools_registry.models import Category, Tool


class CategorySerializer(serializers.ModelSerializer):
    tool_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "order",
            "is_active",
            "tool_count",
        )


class ToolListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Tool
        fields = (
            "id",
            "tool_id",
            "slug",
            "category",
            "name",
            "description",
            "version",
            "premium",
            "adsense_slot",
            "icon",
            "order",
            "usage_count",
            "capabilities",
            "source",
        )


class ToolDetailSerializer(ToolListSerializer):
    class Meta(ToolListSerializer.Meta):
        fields = ToolListSerializer.Meta.fields + (
            "seo_title",
            "seo_description",
            "seo_keywords",
            "schema_type",
            "faq",
            "howto_steps",
            "related_slugs",
            "created_at",
            "updated_at",
        )
