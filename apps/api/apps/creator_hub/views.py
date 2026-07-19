from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.creator_hub.models import CreatorRevenueShareStub, CreatorSubmission, CreatorUsageStat
from apps.creator_hub.serializers import (
    CreatorProfileSerializer,
    CreatorRevenueShareStubSerializer,
    CreatorSubmissionSerializer,
    CreatorUsageStatSerializer,
)
from apps.creator_hub.services import (
    approve_submission,
    accrue_revenue_shares,
    get_or_create_creator_profile,
    reject_submission,
    rollup_creator_usage,
    submit_for_review,
)


class CreatorProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = get_or_create_creator_profile(request.user)
        return success_response(CreatorProfileSerializer(profile).data)

    def patch(self, request):
        profile = get_or_create_creator_profile(request.user)
        ser = CreatorProfileSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)


class CreatorSubmissionListCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = get_or_create_creator_profile(request.user)
        qs = CreatorSubmission.objects.filter(creator=profile).order_by("-updated_at")
        return success_response(CreatorSubmissionSerializer(qs, many=True).data)

    def post(self, request):
        profile = get_or_create_creator_profile(request.user)
        ser = CreatorSubmissionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = CreatorSubmission.objects.create(
            creator=profile,
            type=ser.validated_data["type"],
            payload=ser.validated_data.get("payload") or {},
            status=CreatorSubmission.Status.DRAFT,
        )
        return success_response(
            CreatorSubmissionSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class CreatorSubmissionSubmitView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk: int):
        profile = get_or_create_creator_profile(request.user)
        try:
            submission = CreatorSubmission.objects.get(pk=pk, creator=profile)
        except CreatorSubmission.DoesNotExist as exc:
            raise NotFound("Submission not found") from exc
        try:
            submission = submit_for_review(submission)
        except ValueError as exc:
            raise ValidationError({"status": str(exc)}) from exc
        return success_response(CreatorSubmissionSerializer(submission).data)


class AdminCreatorSubmissionListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = CreatorSubmission.objects.select_related("creator", "tool_spec").order_by(
            "-updated_at"
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(CreatorSubmissionSerializer(qs[:200], many=True).data)


class AdminCreatorSubmissionApproveView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            submission = CreatorSubmission.objects.select_related("creator", "creator__user").get(
                pk=pk
            )
        except CreatorSubmission.DoesNotExist as exc:
            raise NotFound("Submission not found") from exc
        notes = request.data.get("notes") or request.data.get("reviewer_notes") or ""
        submission = approve_submission(submission, reviewer=request.user, notes=str(notes))
        return success_response(CreatorSubmissionSerializer(submission).data)


class AdminCreatorSubmissionRejectView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            submission = CreatorSubmission.objects.get(pk=pk)
        except CreatorSubmission.DoesNotExist as exc:
            raise NotFound("Submission not found") from exc
        notes = request.data.get("notes") or request.data.get("reviewer_notes") or ""
        submission = reject_submission(submission, notes=str(notes))
        return success_response(CreatorSubmissionSerializer(submission).data)


class CreatorUsageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = get_or_create_creator_profile(request.user)
        qs = CreatorUsageStat.objects.filter(submission__creator=profile).order_by("-period")
        return success_response(CreatorUsageStatSerializer(qs[:100], many=True).data)


class CreatorPayoutsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = get_or_create_creator_profile(request.user)
        qs = CreatorRevenueShareStub.objects.filter(creator=profile).order_by("-period")
        return success_response(CreatorRevenueShareStubSerializer(qs[:100], many=True).data)


class AdminCreatorRollupView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        from datetime import date, timedelta

        from django.utils import timezone

        today = timezone.now().date()
        raw_start = request.data.get("period_start")
        raw_end = request.data.get("period_end")
        if raw_start and raw_end:
            period_start = date.fromisoformat(str(raw_start)[:10])
            period_end = date.fromisoformat(str(raw_end)[:10])
        else:
            period_end = today
            period_start = today - timedelta(days=30)
        result = rollup_creator_usage(period_start, period_end)
        shares = accrue_revenue_shares(period_start, period_end)
        return success_response({**result, **shares})
