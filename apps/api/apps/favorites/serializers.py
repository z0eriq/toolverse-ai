from rest_framework import serializers

from apps.favorites.models import Favorite
from apps.tools_registry.serializers import ToolListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    tool = ToolListSerializer(read_only=True)
    tool_id = serializers.CharField(write_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "tool", "tool_id", "created_at")
        read_only_fields = ("id", "tool", "created_at")
