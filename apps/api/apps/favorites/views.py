from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.favorites.models import Favorite
from apps.favorites.serializers import FavoriteSerializer
from apps.tools_registry.models import Tool


class FavoriteListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related("tool", "tool__category")

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        tool_id = request.data.get("tool_id")
        try:
            tool = Tool.objects.get(tool_id=tool_id, is_active=True)
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        fav, _ = Favorite.objects.get_or_create(user=request.user, tool=tool)
        return success_response(FavoriteSerializer(fav).data, status_code=status.HTTP_201_CREATED)


class FavoriteDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, tool_id: str):
        deleted, _ = Favorite.objects.filter(user=request.user, tool__tool_id=tool_id).delete()
        return success_response({"deleted": bool(deleted)})
