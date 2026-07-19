from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.programmatic_seo.models import ProgrammaticPage
from apps.programmatic_seo.serializers import (
    ProgrammaticPageDetailSerializer,
    ProgrammaticPageListSerializer,
)


class ProgrammaticPageListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProgrammaticPageListSerializer
    queryset = ProgrammaticPage.objects.filter(status=ProgrammaticPage.Status.PUBLISHED)
    filterset_fields = ("page_type", "category_slug", "topic", "audience")
    search_fields = ("slug", "keyword", "topic")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return success_response(ser.data)


class ProgrammaticPageByPathView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        path = (request.query_params.get("path") or "").strip().strip("/")
        if not path:
            raise ValidationError({"path": "Required query parameter"})
        try:
            page = ProgrammaticPage.objects.get(
                slug=path,
                status=ProgrammaticPage.Status.PUBLISHED,
            )
        except ProgrammaticPage.DoesNotExist as exc:
            raise NotFound("Programmatic page not found") from exc
        return success_response(ProgrammaticPageDetailSerializer(page).data)


class ProgrammaticSitemapView(APIView):
    """Lightweight sitemap payload for Next.js (reuse list semantics)."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AnonRateThrottle,)

    def get(self, request):
        pages = ProgrammaticPage.objects.filter(
            status=ProgrammaticPage.Status.PUBLISHED
        ).values("slug", "page_type", "updated_at")
        payload = [
            {
                "path": p["slug"],
                "page_type": p["page_type"],
                "updated_at": p["updated_at"].isoformat(),
            }
            for p in pages
        ]
        return success_response(payload)
