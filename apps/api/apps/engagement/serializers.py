from rest_framework import serializers

from apps.engagement.models import (
    Collection,
    CollectionItem,
    SavedOutput,
    ToolComment,
    ToolReview,
)
from apps.tools_registry.models import Tool


class SavedOutputSerializer(serializers.ModelSerializer):
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)
    tool_id = serializers.CharField(write_only=True, required=False)
    tool = serializers.PrimaryKeyRelatedField(
        queryset=Tool.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = SavedOutput
        fields = (
            "id",
            "tool",
            "tool_id",
            "tool_slug",
            "title",
            "content",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "tool_slug")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("tool") and not self.initial_data.get("tool_id"):
            raise serializers.ValidationError({"tool_id": "tool or tool_id is required"})
        return attrs

    def create(self, validated_data):
        tool_id = validated_data.pop("tool_id", None)
        if tool_id and "tool" not in validated_data:
            validated_data["tool"] = Tool.objects.get(tool_id=tool_id, is_active=True)
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CollectionItemSerializer(serializers.ModelSerializer):
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)
    tool_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CollectionItem
        fields = ("id", "tool", "tool_id", "tool_slug", "order", "created_at")
        read_only_fields = ("id", "created_at", "tool_slug")


class CollectionSerializer(serializers.ModelSerializer):
    items = CollectionItemSerializer(many=True, read_only=True)
    owner_username = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_public",
            "public_slug",
            "owner_username",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "public_slug", "owner_username", "created_at", "updated_at")

    def get_owner_username(self, obj: Collection) -> str:
        profile = getattr(obj.user, "profile", None)
        if profile and profile.public_username and profile.is_public:
            return profile.public_username
        return ""


class ToolReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True, default="")
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)
    tool_id = serializers.CharField(write_only=True, required=False)
    tool = serializers.PrimaryKeyRelatedField(
        queryset=Tool.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = ToolReview
        fields = (
            "id",
            "tool",
            "tool_id",
            "tool_slug",
            "rating",
            "title",
            "body",
            "status",
            "user_name",
            "created_at",
        )
        read_only_fields = ("id", "status", "user_name", "created_at", "tool_slug")

    def validate(self, attrs):
        if not attrs.get("tool") and not self.initial_data.get("tool_id"):
            raise serializers.ValidationError({"tool_id": "tool or tool_id is required"})
        return attrs

    def create(self, validated_data):
        tool_id = validated_data.pop("tool_id", None)
        if tool_id and "tool" not in validated_data:
            validated_data["tool"] = Tool.objects.get(tool_id=tool_id, is_active=True)
        validated_data["user"] = self.context["request"].user
        validated_data["status"] = ToolReview.Status.PENDING
        return super().create(validated_data)


class ToolCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True, default="")
    tool_slug = serializers.CharField(source="tool.slug", read_only=True)
    tool_id = serializers.CharField(write_only=True, required=False)
    tool = serializers.PrimaryKeyRelatedField(
        queryset=Tool.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = ToolComment
        fields = (
            "id",
            "tool",
            "tool_id",
            "tool_slug",
            "body",
            "parent",
            "status",
            "user_name",
            "created_at",
        )
        read_only_fields = ("id", "status", "user_name", "created_at", "tool_slug")

    def validate(self, attrs):
        if not attrs.get("tool") and not self.initial_data.get("tool_id"):
            raise serializers.ValidationError({"tool_id": "tool or tool_id is required"})
        return attrs

    def create(self, validated_data):
        tool_id = validated_data.pop("tool_id", None)
        if tool_id and "tool" not in validated_data:
            validated_data["tool"] = Tool.objects.get(tool_id=tool_id, is_active=True)
        validated_data["user"] = self.context["request"].user
        validated_data["status"] = ToolComment.Status.PENDING
        return super().create(validated_data)
