from rest_framework import serializers

from apps.programmatic_seo.models import ProgrammaticPage


class ProgrammaticPageListSerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)

    class Meta:
        model = ProgrammaticPage
        fields = (
            "slug",
            "path",
            "path_pattern",
            "title",
            "description",
            "page_type",
            "topic",
            "category_slug",
            "audience",
            "keyword",
            "status",
            "related_tool_ids",
            "seo_title",
            "seo_description",
            "updated_at",
        )


class ProgrammaticPageDetailSerializer(ProgrammaticPageListSerializer):
    class Meta(ProgrammaticPageListSerializer.Meta):
        fields = ProgrammaticPageListSerializer.Meta.fields + (
            "body",
            "seo_keywords",
            "created_at",
        )
