from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.backlinks.models import BacklinkCampaign, BacklinkOpportunity, BacklinkTarget
from apps.backlinks.serializers import (
    BacklinkCampaignSerializer,
    BacklinkOpportunitySerializer,
    BacklinkTargetSerializer,
)
from apps.common.exceptions import success_response

_ALLOWED_TRANSITIONS = {
    BacklinkOpportunity.Status.OPEN: {
        BacklinkOpportunity.Status.OUTREACH,
        BacklinkOpportunity.Status.DISMISSED,
    },
    BacklinkOpportunity.Status.OUTREACH: {
        BacklinkOpportunity.Status.WON,
        BacklinkOpportunity.Status.LOST,
        BacklinkOpportunity.Status.DISMISSED,
    },
    BacklinkOpportunity.Status.WON: set(),
    BacklinkOpportunity.Status.LOST: {BacklinkOpportunity.Status.OUTREACH},
    BacklinkOpportunity.Status.DISMISSED: {BacklinkOpportunity.Status.OPEN},
}


class BacklinkTargetListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = BacklinkTarget.objects.all().order_by("-created_at")
        return success_response(BacklinkTargetSerializer(qs[:200], many=True).data)

    def post(self, request):
        ser = BacklinkTargetSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(
            BacklinkTargetSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class BacklinkCampaignListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = BacklinkCampaign.objects.select_related("target").order_by("-created_at")
        return success_response(BacklinkCampaignSerializer(qs[:200], many=True).data)

    def post(self, request):
        ser = BacklinkCampaignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(
            BacklinkCampaignSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class BacklinkOpportunityListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = BacklinkOpportunity.objects.select_related("target", "campaign").order_by(
            "-priority", "-created_at"
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(BacklinkOpportunitySerializer(qs[:200], many=True).data)

    def post(self, request):
        ser = BacklinkOpportunitySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(
            BacklinkOpportunitySerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class BacklinkOpportunityStatusView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            opp = BacklinkOpportunity.objects.get(pk=pk)
        except BacklinkOpportunity.DoesNotExist as exc:
            raise NotFound("Backlink opportunity not found") from exc
        new_status = request.data.get("status")
        valid = {c.value for c in BacklinkOpportunity.Status}
        if new_status not in valid:
            raise ValidationError({"status": f"Must be one of {sorted(valid)}"})
        allowed = _ALLOWED_TRANSITIONS.get(opp.status, set())
        if new_status != opp.status and new_status not in allowed:
            raise ValidationError(
                {
                    "status": (
                        f"Cannot transition from {opp.status} to {new_status}. "
                        f"Allowed: {sorted(allowed)}"
                    )
                }
            )
        opp.status = new_status
        opp.save(update_fields=["status", "updated_at"])
        return success_response(BacklinkOpportunitySerializer(opp).data)
