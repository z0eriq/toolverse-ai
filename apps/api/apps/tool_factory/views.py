from __future__ import annotations

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.audit import log_audit
from apps.common.exceptions import success_response
from apps.tool_factory.models import ToolSpec
from apps.tool_factory.serializers import ToolSpecSerializer
from apps.tool_factory.services import build_tool_from_spec
from apps.tool_factory.tasks import build_tool_from_spec_task


class ToolSpecListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = ToolSpecSerializer
    queryset = ToolSpec.objects.all()
    search_fields = ("slug",)
    filterset_fields = ("status", "recipe", "category_slug", "is_viral")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return success_response(ser.data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(created_by=request.user)
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class ToolSpecDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = ToolSpecSerializer
    queryset = ToolSpec.objects.all()
    http_method_names = ["get", "patch", "put", "head", "options"]

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class ToolSpecBuildView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            ToolSpec.objects.get(pk=pk)
        except ToolSpec.DoesNotExist as exc:
            raise NotFound("ToolSpec not found") from exc

        async_mode = str(request.data.get("async", "")).lower() in {"1", "true", "yes"}
        if async_mode:
            task = build_tool_from_spec_task.delay(pk, user_id=request.user.pk)
            return success_response({"queued": True, "task_id": task.id, "spec_id": pk})

        try:
            result = build_tool_from_spec(pk, user=request.user)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError({"build": str(exc)}) from exc

        log_audit(
            request,
            "tool_factory.build",
            resource_type="tool_factory.ToolSpec",
            resource_id=pk,
            meta={"slug": result.get("slug"), "tool_id": result.get("tool_id")},
        )
        return success_response(result)


class ToolSpecPublishView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            spec = ToolSpec.objects.get(pk=pk)
        except ToolSpec.DoesNotExist as exc:
            raise NotFound("ToolSpec not found") from exc

        try:
            result = build_tool_from_spec(pk, user=request.user)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError({"publish": str(exc)}) from exc

        spec.refresh_from_db()
        if spec.status != ToolSpec.Status.PUBLISHED:
            spec.status = ToolSpec.Status.PUBLISHED
            spec.save(update_fields=["status", "updated_at"])

        log_audit(
            request,
            "tool_factory.publish",
            resource_type="tool_factory.ToolSpec",
            resource_id=pk,
            meta={"slug": result.get("slug"), "tool_id": result.get("tool_id")},
        )
        return success_response({**result, "status": ToolSpec.Status.PUBLISHED})
