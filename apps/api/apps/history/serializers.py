from rest_framework import serializers

from apps.history.models import ToolHistory
from apps.tools_registry.serializers import ToolListSerializer


class ToolHistorySerializer(serializers.ModelSerializer):
    tool = ToolListSerializer(read_only=True)
    tool_id = serializers.CharField(write_only=True)

    class Meta:
        model = ToolHistory
        fields = ("id", "tool", "tool_id", "action", "meta", "created_at")
        read_only_fields = ("id", "tool", "created_at")
