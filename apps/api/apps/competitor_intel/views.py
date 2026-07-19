from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.competitor_intel.models import CompetitorDomain, CompetitorOpportunity
from apps.competitor_intel.serializers import (
    CompetitorDomainSerializer,
    CompetitorOpportunitySerializer,
)
from apps.competitor_intel.services import recompute_competitor_opportunities


class CompetitorDomainListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = CompetitorDomain.objects.all().order_by("domain")
        return success_response(CompetitorDomainSerializer(qs, many=True).data)

    def post(self, request):
        ser = CompetitorDomainSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(
            CompetitorDomainSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class CompetitorDomainDetailView(APIView):
    permission_classes = (IsAdminRole,)

    def get_object(self, pk: int) -> CompetitorDomain:
        try:
            return CompetitorDomain.objects.get(pk=pk)
        except CompetitorDomain.DoesNotExist as exc:
            raise NotFound("Competitor domain not found") from exc

    def get(self, request, pk: int):
        return success_response(CompetitorDomainSerializer(self.get_object(pk)).data)

    def patch(self, request, pk: int):
        obj = self.get_object(pk)
        ser = CompetitorDomainSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def delete(self, request, pk: int):
        self.get_object(pk).delete()
        return success_response({"deleted": True})


class CompetitorOpportunityListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = CompetitorOpportunity.objects.select_related("competitor").order_by(
            "-gap_score", "-created_at"
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(CompetitorOpportunitySerializer(qs[:200], many=True).data)


class CompetitorRecomputeView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        result = recompute_competitor_opportunities()
        return success_response(result, status_code=status.HTTP_201_CREATED)
