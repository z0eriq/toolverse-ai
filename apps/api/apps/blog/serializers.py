from rest_framework import serializers

from apps.blog.models import BlogPost, BlogTag


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ("slug", "name")


class BlogPostListSerializer(serializers.ModelSerializer):
    tags = BlogTagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source="author.name", read_only=True, default="")

    class Meta:
        model = BlogPost
        fields = (
            "slug",
            "title",
            "excerpt",
            "cover_image",
            "published_at",
            "tags",
            "author_name",
            "seo_title",
            "seo_description",
        )


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ("content",)
