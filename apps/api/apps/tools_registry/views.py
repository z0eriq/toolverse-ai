from django.db.models import Count, F, Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.tools_registry.cache import (
    TOOL_DETAIL_KEY,
    TOOLS_LIST_KEY,
    cache_get,
    cache_set,
)
from apps.tools_registry.models import Category, Tool
from apps.tools_registry.serializers import (
    CategorySerializer,
    ToolDetailSerializer,
    ToolListSerializer,
)

TOOLS_LIST_TTL = 60
TOOL_DETAIL_TTL = 120


class ToolThrottle(UserRateThrottle):
    scope = "tool"


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return (
            Category.objects.filter(is_active=True)
            .annotate(tool_count=Count("tools", filter=Q(tools__is_active=True)))
            .order_by("order", "slug")
        )

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return success_response(CategorySerializer(qs, many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return success_response(CategorySerializer(self.get_object()).data)


class ToolViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "slug"
    permission_classes = (permissions.AllowAny,)
    search_fields = ("search_document", "tool_id", "slug")
    filterset_fields = ("category__slug", "premium")
    ordering_fields = ("order", "usage_count", "slug", "created_at")
    ordering = ("order", "slug")

    def get_queryset(self):
        qs = Tool.objects.filter(is_active=True).select_related("category")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(search_document__icontains=q.lower())
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ToolDetailSerializer
        return ToolListSerializer

    def list(self, request, *args, **kwargs):
        query = request.META.get("QUERY_STRING", "") or ""
        cache_key = f"{TOOLS_LIST_KEY}:{query}" if query else TOOLS_LIST_KEY
        cached = cache_get(cache_key)
        if cached is not None:
            return Response(cached)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            response = self.get_paginated_response(serializer.data)
            cache_set(cache_key, response.data, timeout=TOOLS_LIST_TTL)
            return response
        response = success_response(serializer.data)
        cache_set(cache_key, response.data, timeout=TOOLS_LIST_TTL)
        return response

    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs.get(self.lookup_field) or kwargs.get(self.lookup_field)
        cache_key = TOOL_DETAIL_KEY.format(slug=slug)
        cached = cache_get(cache_key)
        if cached is not None:
            return Response(cached)

        tool = self.get_object()
        response = success_response(ToolDetailSerializer(tool).data)
        cache_set(cache_key, response.data, timeout=TOOL_DETAIL_TTL)
        return response

    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def track(self, request, slug=None):
        # Cache invalidation on track is intentionally skipped (high write volume).
        Tool.objects.filter(slug=slug, is_active=True).update(usage_count=F("usage_count") + 1)
        return success_response({"tracked": True})

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def related(self, request, slug=None):
        from apps.recommendations.services import get_related_tools

        limit_raw = request.query_params.get("limit", "6")
        try:
            limit = max(1, min(int(limit_raw), 24))
        except (TypeError, ValueError):
            limit = 6
        tools = get_related_tools(slug or "", limit=limit)
        return success_response(ToolListSerializer(tools, many=True).data)


class SitemapToolsView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AnonRateThrottle,)

    def get(self, request):
        tools = (
            Tool.objects.filter(is_active=True)
            .select_related("category")
            .values("slug", "category__slug", "updated_at", "premium")
        )
        payload = [
            {
                "slug": t["slug"],
                "category": t["category__slug"],
                "updated_at": t["updated_at"].isoformat(),
                "premium": t["premium"],
            }
            for t in tools
        ]
        return success_response(payload)
