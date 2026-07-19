from __future__ import annotations

from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.seo_optimizer.autopilot import apply_page_issue, scan_seo_autopilot
from apps.seo_optimizer.health import compute_seo_health, recompute_all_seo_health
from apps.seo_optimizer.models import (
    SeoHealthScore,
    SeoOpportunityTask,
    SeoPageIssue,
    SeoRecommendation,
)
from apps.seo_optimizer.services import analyze_page, generate_seo_opportunity_tasks


class SeoRecommendationSerializer(serializers.ModelSerializer):
    tool_slug = serializers.CharField(source="tool.slug", read_only=True, allow_null=True)

    class Meta:
        model = SeoRecommendation
        fields = (
            "id",
            "path",
            "tool",
            "tool_slug",
            "type",
            "severity",
            "suggestion",
            "rationale",
            "status",
            "evidence",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SeoAnalyzeView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        path = request.data.get("path") or request.data.get("url")
        if not path:
            raise ValidationError({"path": "Required"})
        recs = analyze_page(str(path))
        return success_response(
            SeoRecommendationSerializer(recs, many=True).data,
            status_code=status.HTTP_201_CREATED,
        )


class SeoRecommendationListView(generics.ListAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = SeoRecommendationSerializer
    queryset = SeoRecommendation.objects.select_related("tool").all()
    filterset_fields = ("status", "type", "severity", "path")
    search_fields = ("path", "suggestion")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return success_response(ser.data)


class SeoRecommendationAcceptView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            rec = SeoRecommendation.objects.get(pk=pk)
        except SeoRecommendation.DoesNotExist as exc:
            raise NotFound("Recommendation not found") from exc
        rec.status = SeoRecommendation.Status.ACCEPTED
        rec.save(update_fields=["status", "updated_at"])
        return success_response(SeoRecommendationSerializer(rec).data)


class SeoRecommendationDismissView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            rec = SeoRecommendation.objects.get(pk=pk)
        except SeoRecommendation.DoesNotExist as exc:
            raise NotFound("Recommendation not found") from exc
        rec.status = SeoRecommendation.Status.DISMISSED
        rec.save(update_fields=["status", "updated_at"])
        return success_response(SeoRecommendationSerializer(rec).data)


class SeoHealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoHealthScore
        fields = (
            "id",
            "path",
            "metadata",
            "schema",
            "internal_links",
            "content_quality",
            "keyword_coverage",
            "performance",
            "overall",
            "recommendations",
            "analyzed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SeoHealthListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = SeoHealthScore.objects.all().order_by("-overall", "path")
        path = request.query_params.get("path")
        if path:
            qs = qs.filter(path=path)
        return success_response(SeoHealthScoreSerializer(qs[:200], many=True).data)

    def post(self, request):
        path = request.data.get("path") or request.data.get("url")
        if not path:
            raise ValidationError({"path": "Required"})
        perf = request.data.get("perf")
        score = compute_seo_health(str(path), perf=perf)
        return success_response(
            SeoHealthScoreSerializer(score).data,
            status_code=status.HTTP_201_CREATED,
        )


class SeoHealthRecomputeView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        result = recompute_all_seo_health()
        return success_response(result)


class SeoOpportunityTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoOpportunityTask
        fields = (
            "id",
            "source",
            "title",
            "rationale",
            "priority",
            "status",
            "suggested_action",
            "path",
            "keyword",
            "tool_opportunity",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "source",
            "title",
            "rationale",
            "suggested_action",
            "path",
            "keyword",
            "tool_opportunity",
            "created_at",
            "updated_at",
        )


class SeoOpportunityTaskListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = SeoOpportunityTask.objects.select_related(
            "keyword", "tool_opportunity"
        ).order_by("-priority", "-created_at")
        status_filter = request.query_params.get("status")
        source = request.query_params.get("source")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source:
            qs = qs.filter(source=source)
        return success_response(
            SeoOpportunityTaskSerializer(qs[:200], many=True).data
        )


class SeoOpportunityTaskDetailView(APIView):
    permission_classes = (IsAdminRole,)

    def patch(self, request, pk: int):
        try:
            task = SeoOpportunityTask.objects.get(pk=pk)
        except SeoOpportunityTask.DoesNotExist as exc:
            raise NotFound("SEO opportunity task not found") from exc
        ser = SeoOpportunityTaskSerializer(task, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        if "status" in ser.validated_data:
            task.status = ser.validated_data["status"]
        if "priority" in ser.validated_data:
            task.priority = ser.validated_data["priority"]
        task.save()
        return success_response(SeoOpportunityTaskSerializer(task).data)


class SeoOpportunityTaskGenerateView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        result = generate_seo_opportunity_tasks()
        return success_response(result, status_code=status.HTTP_201_CREATED)


class SeoPageIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeoPageIssue
        fields = (
            "id",
            "run",
            "path",
            "issue_type",
            "severity",
            "suggestion",
            "status",
            "evidence",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SeoAutopilotScanView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        run = scan_seo_autopilot()
        return success_response(
            {
                "id": run.pk,
                "status": run.status,
                "issues_created": run.issues_created,
                "summary": run.summary,
                "error": run.error,
                "finished_at": run.finished_at,
            },
            status_code=status.HTTP_201_CREATED,
        )


class SeoPageIssueListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = SeoPageIssue.objects.select_related("run").order_by("-created_at")
        status_filter = request.query_params.get("status")
        issue_type = request.query_params.get("issue_type")
        path = request.query_params.get("path")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if issue_type:
            qs = qs.filter(issue_type=issue_type)
        if path:
            qs = qs.filter(path=path)
        return success_response(SeoPageIssueSerializer(qs[:200], many=True).data)


class SeoPageIssueApplyView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            issue = SeoPageIssue.objects.get(pk=pk)
        except SeoPageIssue.DoesNotExist as exc:
            raise NotFound("SEO page issue not found") from exc
        issue = apply_page_issue(issue, user=request.user)
        return success_response(SeoPageIssueSerializer(issue).data)


class SeoPageIssueDismissView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            issue = SeoPageIssue.objects.get(pk=pk)
        except SeoPageIssue.DoesNotExist as exc:
            raise NotFound("SEO page issue not found") from exc
        issue.status = SeoPageIssue.Status.DISMISSED
        issue.save(update_fields=["status", "updated_at"])
        return success_response(SeoPageIssueSerializer(issue).data)
