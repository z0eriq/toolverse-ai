from __future__ import annotations

from rest_framework import serializers
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.search_console.models import IndexedUrl
from apps.search_console.services import overview_aggregates, top_pages, top_queries


class GSCOverviewView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        days = int(request.query_params.get("days") or 28)
        return success_response(overview_aggregates(days=days))


class GSCQueriesView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        days = int(request.query_params.get("days") or 28)
        limit = int(request.query_params.get("limit") or 50)
        return success_response(top_queries(days=days, limit=limit))


class GSCPagesView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        days = int(request.query_params.get("days") or 28)
        limit = int(request.query_params.get("limit") or 50)
        return success_response(top_pages(days=days, limit=limit))


class IndexedUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexedUrl
        fields = (
            "id",
            "url_path",
            "status",
            "last_crawled_at",
            "impressions",
            "clicks",
            "position",
            "ranking_delta",
            "created_at",
            "updated_at",
        )


class IndexedUrlListView(APIView):
    """Admin list/filter for IndexedUrl rows."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = IndexedUrl.objects.all()
        status_filter = request.query_params.get("status")
        q = request.query_params.get("q") or request.query_params.get("path")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if q:
            qs = qs.filter(url_path__icontains=q)
        limit = min(int(request.query_params.get("limit") or 100), 500)
        return success_response(IndexedUrlSerializer(qs[:limit], many=True).data)
