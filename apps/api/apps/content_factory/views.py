from __future__ import annotations

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.ai_providers.base import AIProviderError
from apps.common.audit import log_audit
from apps.common.exceptions import success_response
from apps.content_factory.models import ContentItem, PromptTemplate
from apps.content_factory.serializers import (
    ContentGenerateSerializer,
    ContentItemSerializer,
    PromptTemplateSerializer,
)
from apps.content_factory.services import generate_content, publish_content, queue_regenerate


class PromptTemplateListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = PromptTemplateSerializer
    queryset = PromptTemplate.objects.all()
    search_fields = ("slug", "name", "purpose")
    filterset_fields = ("purpose", "locale")

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
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class ContentItemListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = ContentItemSerializer
    queryset = ContentItem.objects.select_related("tool", "created_by").all()
    search_fields = ("title", "slug", "target_path")
    filterset_fields = ("status", "locale", "content_type")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return success_response(ser.data)

    def create(self, request, *args, **kwargs):
        # Optional AI generation on create
        if request.data.get("template_slug"):
            gen = ContentGenerateSerializer(data=request.data)
            gen.is_valid(raise_exception=True)
            try:
                content = generate_content(
                    gen.validated_data["template_slug"],
                    gen.validated_data.get("variables") or {},
                    user=request.user,
                    provider=gen.validated_data.get("provider") or None,
                    model=gen.validated_data.get("model") or None,
                )
            except PromptTemplate.DoesNotExist as exc:
                raise NotFound("Prompt template not found") from exc
            except AIProviderError as exc:
                raise ValidationError({"ai": str(exc)}) from exc
            return success_response(
                ContentItemSerializer(content).data,
                status_code=status.HTTP_201_CREATED,
            )

        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(created_by=request.user)
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class ContentItemDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = ContentItemSerializer
    queryset = ContentItem.objects.select_related("tool", "created_by").all()

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


class ContentPublishView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            content = ContentItem.objects.get(pk=pk)
        except ContentItem.DoesNotExist as exc:
            raise NotFound("Content not found") from exc
        publish_content(content)
        log_audit(
            request,
            "content_factory.publish",
            resource_type="content_factory.ContentItem",
            resource_id=content.pk,
            meta={"slug": content.slug, "status": content.status},
        )
        return success_response(ContentItemSerializer(content).data)


class ContentRegenerateView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            ContentItem.objects.get(pk=pk)
        except ContentItem.DoesNotExist as exc:
            raise NotFound("Content not found") from exc
        template_slug = request.data.get("template_slug")
        task_id = queue_regenerate(pk, template_slug=template_slug)
        return success_response({"queued": True, "task_id": task_id, "content_id": pk})
