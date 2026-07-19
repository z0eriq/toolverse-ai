from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound

from apps.common.exceptions import success_response
from apps.history.models import ToolHistory
from apps.history.serializers import ToolHistorySerializer
from apps.tools_registry.models import Tool


class HistoryListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ToolHistorySerializer

    def get_queryset(self):
        return (
            ToolHistory.objects.filter(user=self.request.user)
            .select_related("tool", "tool__category")[:100]
        )

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        tool_id = request.data.get("tool_id")
        try:
            tool = Tool.objects.get(tool_id=tool_id, is_active=True)
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        entry = ToolHistory.objects.create(
            user=request.user,
            tool=tool,
            action=request.data.get("action", "run"),
            meta=request.data.get("meta") or {},
        )
        Tool.objects.filter(pk=tool.pk).update(usage_count=tool.usage_count + 1)
        return success_response(
            ToolHistorySerializer(entry).data, status_code=status.HTTP_201_CREATED
        )
