from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.audit import log_audit
from apps.common.exceptions import success_response
from apps.engagement.models import Collection, CollectionItem, SavedOutput, ToolComment, ToolReview
from apps.engagement.serializers import (
    CollectionItemSerializer,
    CollectionSerializer,
    SavedOutputSerializer,
    ToolCommentSerializer,
    ToolReviewSerializer,
)
from apps.tools_registry.models import Tool


class SavedOutputListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SavedOutputSerializer

    def get_queryset(self):
        return SavedOutput.objects.filter(user=self.request.user).select_related(
            "tool", "tool__category"
        )

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = ser.save()
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class SavedOutputDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SavedOutputSerializer

    def get_queryset(self):
        return SavedOutput.objects.filter(user=self.request.user).select_related(
            "tool", "tool__category"
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response({"deleted": True})


class CollectionListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user).prefetch_related(
            "items", "items__tool", "items__tool__category"
        )

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user).prefetch_related(
            "items", "items__tool", "items__tool__category"
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response({"deleted": True})


class CollectionItemAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, slug: str):
        try:
            collection = Collection.objects.get(user=request.user, slug=slug)
        except Collection.DoesNotExist as exc:
            raise NotFound("Collection not found") from exc
        tool_id = request.data.get("tool_id")
        try:
            tool = Tool.objects.get(tool_id=tool_id, is_active=True)
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        order = int(request.data.get("order") or 0)
        item, _ = CollectionItem.objects.update_or_create(
            collection=collection,
            tool=tool,
            defaults={"order": order},
        )
        return success_response(
            CollectionItemSerializer(item).data,
            status_code=status.HTTP_201_CREATED,
        )


class CollectionItemRemoveView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, slug: str, tool_id: str):
        deleted, _ = CollectionItem.objects.filter(
            collection__user=request.user,
            collection__slug=slug,
            tool__tool_id=tool_id,
        ).delete()
        return success_response({"deleted": bool(deleted)})


class ToolReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ToolReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = ToolReview.objects.filter(status=ToolReview.Status.APPROVED).select_related(
            "user", "tool", "tool__category"
        )
        tool_slug = self.request.query_params.get("tool")
        if tool_slug:
            qs = qs.filter(tool__slug=tool_slug)
        return qs

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = ser.save()
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        except Exception as exc:  # noqa: BLE001
            if "unique" in str(exc).lower():
                raise ValidationError({"tool": "You already reviewed this tool"}) from exc
            raise
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class ToolReviewModerateView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            review = ToolReview.objects.select_related("user", "tool").get(pk=pk)
        except ToolReview.DoesNotExist as exc:
            raise NotFound("Review not found") from exc
        new_status = request.data.get("status")
        if new_status not in {
            ToolReview.Status.APPROVED,
            ToolReview.Status.REJECTED,
            ToolReview.Status.PENDING,
        }:
            raise ValidationError({"status": "Must be pending, approved, or rejected"})
        review.status = new_status
        review.save(update_fields=["status", "updated_at"])
        log_audit(
            request,
            "engagement.review.moderate",
            resource_type="engagement.ToolReview",
            resource_id=review.pk,
            meta={"status": new_status, "tool_id": review.tool_id},
        )
        return success_response(ToolReviewSerializer(review).data)


class ToolCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = ToolCommentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = ToolComment.objects.filter(status=ToolComment.Status.APPROVED).select_related(
            "user", "tool", "tool__category", "parent"
        )
        tool_slug = self.request.query_params.get("tool")
        if tool_slug:
            qs = qs.filter(tool__slug=tool_slug)
        return qs

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = ser.save()
        except Tool.DoesNotExist as exc:
            raise NotFound("Tool not found") from exc
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class ToolCommentModerateView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            comment = ToolComment.objects.select_related("user", "tool").get(pk=pk)
        except ToolComment.DoesNotExist as exc:
            raise NotFound("Comment not found") from exc
        new_status = request.data.get("status")
        if new_status not in {
            ToolComment.Status.APPROVED,
            ToolComment.Status.REJECTED,
            ToolComment.Status.PENDING,
        }:
            raise ValidationError({"status": "Must be pending, approved, or rejected"})
        comment.status = new_status
        comment.save(update_fields=["status", "updated_at"])
        log_audit(
            request,
            "engagement.comment.moderate",
            resource_type="engagement.ToolComment",
            resource_id=comment.pk,
            meta={"status": new_status, "tool_id": comment.tool_id},
        )
        return success_response(ToolCommentSerializer(comment).data)
