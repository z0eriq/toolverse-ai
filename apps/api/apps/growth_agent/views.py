from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.growth_agent.actions import execute_growth_action
from apps.growth_agent.models import GrowthAction, GrowthInsight
from apps.growth_agent.serializers import (
    GrowthActionSerializer,
    GrowthAgentRunSerializer,
    GrowthInsightSerializer,
    GrowthTaskSerializer,
)
from apps.growth_agent.services import run_growth_agent


class GrowthAgentRunListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        from apps.growth_agent.models import GrowthAgentRun

        qs = GrowthAgentRun.objects.all().order_by("-created_at")[:50]
        return success_response(GrowthAgentRunSerializer(qs, many=True).data)

    def post(self, request):
        run = run_growth_agent()
        return success_response(
            GrowthAgentRunSerializer(run).data,
            status_code=status.HTTP_201_CREATED,
        )


class GrowthInsightListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = GrowthInsight.objects.all().order_by("-priority", "-created_at")
        status_filter = request.query_params.get("status")
        category = request.query_params.get("category")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if category:
            qs = qs.filter(category=category)
        return success_response(GrowthInsightSerializer(qs[:200], many=True).data)


class GrowthInsightAcceptView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            insight = GrowthInsight.objects.get(pk=pk)
        except GrowthInsight.DoesNotExist as exc:
            raise NotFound("Insight not found") from exc
        insight.status = GrowthInsight.Status.ACCEPTED
        insight.save(update_fields=["status", "updated_at"])
        return success_response(GrowthInsightSerializer(insight).data)


class GrowthInsightDismissView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            insight = GrowthInsight.objects.get(pk=pk)
        except GrowthInsight.DoesNotExist as exc:
            raise NotFound("Insight not found") from exc
        insight.status = GrowthInsight.Status.DISMISSED
        insight.save(update_fields=["status", "updated_at"])
        return success_response(GrowthInsightSerializer(insight).data)


class GrowthTaskListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        from apps.growth_agent.models import GrowthTask

        qs = GrowthTask.objects.select_related("insight").order_by(
            "-priority", "-created_at"
        )
        status_filter = request.query_params.get("status")
        category = request.query_params.get("category")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if category:
            qs = qs.filter(category=category)
        return success_response(GrowthTaskSerializer(qs[:200], many=True).data)


class GrowthTaskAcceptView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        from apps.growth_agent.models import GrowthTask

        try:
            task = GrowthTask.objects.get(pk=pk)
        except GrowthTask.DoesNotExist as exc:
            raise NotFound("Growth task not found") from exc
        task.status = GrowthTask.Status.ACCEPTED
        task.save(update_fields=["status", "updated_at"])
        return success_response(GrowthTaskSerializer(task).data)


class GrowthTaskCompleteView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        from apps.growth_agent.models import GrowthTask

        try:
            task = GrowthTask.objects.get(pk=pk)
        except GrowthTask.DoesNotExist as exc:
            raise NotFound("Growth task not found") from exc
        task.status = GrowthTask.Status.DONE
        task.save(update_fields=["status", "updated_at"])
        return success_response(GrowthTaskSerializer(task).data)


class GrowthActionListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = GrowthAction.objects.select_related("task").order_by("-created_at")
        status_filter = request.query_params.get("status")
        action_type = request.query_params.get("action_type")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if action_type:
            qs = qs.filter(action_type=action_type)
        return success_response(GrowthActionSerializer(qs[:200], many=True).data)


class GrowthActionApproveView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            action = GrowthAction.objects.get(pk=pk)
        except GrowthAction.DoesNotExist as exc:
            raise NotFound("Growth action not found") from exc
        if action.status == GrowthAction.Status.REJECTED:
            raise NotFound("Rejected actions cannot be approved")
        action = execute_growth_action(action, user=request.user)
        return success_response(GrowthActionSerializer(action).data)


class GrowthActionRejectView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            action = GrowthAction.objects.get(pk=pk)
        except GrowthAction.DoesNotExist as exc:
            raise NotFound("Growth action not found") from exc
        action.status = GrowthAction.Status.REJECTED
        action.save(update_fields=["status", "updated_at"])
        return success_response(GrowthActionSerializer(action).data)
