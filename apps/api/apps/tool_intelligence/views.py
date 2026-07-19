from __future__ import annotations

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.tool_intelligence.models import ToolOpportunity, ToolPerformanceScore
from apps.tool_intelligence.serializers import (
    ToolOpportunitySerializer,
    ToolPerformanceScoreSerializer,
)
from apps.tool_intelligence.services import queue_opportunity, recompute_tool_performance_scores


class ToolOpportunityListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = ToolOpportunity.objects.all().order_by("-priority_score")
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        limit = min(int(request.query_params.get("limit") or 100), 500)
        return success_response(
            ToolOpportunitySerializer(qs[:limit], many=True).data
        )


class ToolOpportunityQueueView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            opp = ToolOpportunity.objects.get(pk=pk)
        except ToolOpportunity.DoesNotExist as exc:
            raise NotFound("Tool opportunity not found") from exc
        if opp.status == ToolOpportunity.Status.DISMISSED:
            raise ValidationError({"status": "Cannot queue a dismissed opportunity"})
        queue_opportunity(opp, user=request.user)
        opp.refresh_from_db()
        return success_response(ToolOpportunitySerializer(opp).data)


class ToolPerformanceScoreListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        if request.query_params.get("recompute") in {"1", "true", "yes"}:
            recompute_tool_performance_scores()
        qs = ToolPerformanceScore.objects.select_related("tool").order_by(
            "-priority_score"
        )
        limit = min(int(request.query_params.get("limit") or 200), 500)
        return success_response(
            ToolPerformanceScoreSerializer(qs[:limit], many=True).data
        )
