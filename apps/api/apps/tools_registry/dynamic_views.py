from rest_framework import serializers, status
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.tools_registry.dynamic_models import DynamicToolDefinition
from apps.tools_registry.dynamic_runtime import execute_dynamic_pipeline
from apps.tools_registry.publish import publish_dynamic_tool
from apps.tools_registry.serializers import ToolDetailSerializer


class DynamicToolDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicToolDefinition
        fields = (
            "id",
            "slug",
            "category_slug",
            "name",
            "description",
            "version",
            "revision",
            "premium",
            "status",
            "ui_schema",
            "pipeline",
            "seo",
            "faq",
            "howto_steps",
            "capabilities",
            "icon",
            "adsense_slot",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("revision", "published_at", "created_at", "updated_at")


class DynamicToolListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = DynamicToolDefinition.objects.all().order_by("-updated_at")
        return success_response(DynamicToolDefinitionSerializer(qs, many=True).data)

    def post(self, request):
        serializer = DynamicToolDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(created_by=request.user)
        return success_response(
            DynamicToolDefinitionSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class DynamicToolDetailView(APIView):
    permission_classes = (IsAdminRole,)

    def get_object(self, pk: int) -> DynamicToolDefinition:
        return DynamicToolDefinition.objects.get(pk=pk)

    def get(self, request, pk: int):
        return success_response(DynamicToolDefinitionSerializer(self.get_object(pk)).data)

    def patch(self, request, pk: int):
        obj = self.get_object(pk)
        serializer = DynamicToolDefinitionSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data)

    def delete(self, request, pk: int):
        obj = self.get_object(pk)
        obj.status = DynamicToolDefinition.Status.ARCHIVED
        obj.save(update_fields=["status", "updated_at"])
        if hasattr(obj, "published_tool") and obj.published_tool:
            obj.published_tool.is_active = False
            obj.published_tool.save(update_fields=["is_active", "updated_at"])
        return success_response({"archived": True})


class DynamicToolPublishView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        obj = DynamicToolDefinition.objects.get(pk=pk)
        tool = publish_dynamic_tool(obj)
        return success_response(
            {
                "definition": DynamicToolDefinitionSerializer(obj).data,
                "tool": ToolDetailSerializer(tool).data,
            }
        )


class DynamicToolRunView(APIView):
    """Public/authenticated runtime for published dynamic tools."""

    def post(self, request, slug: str):
        from rest_framework.response import Response

        from apps.common.limits import ToolRunLimitExceeded, check_tool_run_limit, increment_tool_run

        user = request.user if request.user.is_authenticated else None
        try:
            check_tool_run_limit(user)
        except ToolRunLimitExceeded as exc:
            return Response(
                {
                    "success": False,
                    "error": {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": exc.detail,
                    },
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            result = execute_dynamic_pipeline(
                slug,
                {"input": request.data.get("input") or request.data},
                user=user,
            )
        except DynamicToolDefinition.DoesNotExist:
            return Response(
                {"success": False, "error": {"message": "Tool not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:  # noqa: BLE001
            return Response(
                {"success": False, "error": {"message": str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        increment_tool_run(user)
        return success_response(result)
