from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.audit import log_audit
from apps.common.exceptions import success_response
from apps.content_factory.autopilot import approve_autopilot_run, run_content_autopilot
from apps.content_factory.models import AutopilotRun
from apps.content_factory.serializers import (
    AutopilotRunCreateSerializer,
    AutopilotRunSerializer,
)
from apps.keywords.models import KeywordOpportunity


class AutopilotRunListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = AutopilotRun.objects.select_related("keyword", "content_item").order_by(
            "-created_at"
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        limit = min(int(request.query_params.get("limit") or 50), 200)
        return success_response(AutopilotRunSerializer(qs[:limit], many=True).data)

    def post(self, request):
        ser = AutopilotRunCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        keyword_id = ser.validated_data["keyword_id"]
        if not KeywordOpportunity.objects.filter(pk=keyword_id).exists():
            raise NotFound("Keyword opportunity not found")

        async_mode = ser.validated_data.get("async_mode") or str(
            request.data.get("async", "")
        ).lower() in {"1", "true", "yes"}

        if async_mode:
            from apps.content_factory.tasks import run_content_autopilot_task

            run = AutopilotRun.objects.create(
                keyword_id=keyword_id,
                status=AutopilotRun.Status.PENDING,
                stage="pending",
            )
            task = run_content_autopilot_task.delay(keyword_id, run_id=run.pk)
            return success_response(
                {
                    "queued": True,
                    "task_id": task.id,
                    "run": AutopilotRunSerializer(run).data,
                },
                status_code=status.HTTP_201_CREATED,
            )

        run = run_content_autopilot(keyword_id)
        return success_response(
            AutopilotRunSerializer(run).data,
            status_code=status.HTTP_201_CREATED,
        )


class AutopilotApproveView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            run = AutopilotRun.objects.select_related("content_item").get(pk=pk)
        except AutopilotRun.DoesNotExist as exc:
            raise NotFound("Autopilot run not found") from exc
        try:
            approve_autopilot_run(run)
        except ValueError as exc:
            raise ValidationError({"content_item": str(exc)}) from exc
        log_audit(
            request,
            "content_factory.autopilot.approve",
            resource_type="content_factory.AutopilotRun",
            resource_id=run.pk,
            meta={"status": run.status},
        )
        return success_response(AutopilotRunSerializer(run).data)
