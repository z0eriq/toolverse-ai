from __future__ import annotations

from django.db.models import Count, Sum
from rest_framework import generics, status
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.campaigns.models import CampaignResultDaily, MarketingCampaign
from apps.campaigns.serializers import (
    CampaignResultDailySerializer,
    MarketingCampaignSerializer,
)
from apps.common.exceptions import success_response


class CampaignListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = MarketingCampaignSerializer
    queryset = MarketingCampaign.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        status_filter = request.query_params.get("status")
        channel = request.query_params.get("channel")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if channel:
            qs = qs.filter(channel=channel)
        return success_response(self.get_serializer(qs[:200], many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = MarketingCampaignSerializer
    queryset = MarketingCampaign.objects.all()
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        ser = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return success_response(ser.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response({"deleted": True})


class CampaignSummaryView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        by_status = list(
            MarketingCampaign.objects.values("status").annotate(count=Count("id")).order_by("status")
        )
        by_channel = list(
            MarketingCampaign.objects.values("channel").annotate(count=Count("id")).order_by("channel")
        )
        results = CampaignResultDaily.objects.aggregate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            conversions=Sum("conversions"),
            revenue_cents=Sum("revenue_cents"),
        )
        open_count = MarketingCampaign.objects.filter(
            status__in=(MarketingCampaign.Status.ACTIVE, MarketingCampaign.Status.DRAFT)
        ).count()
        return success_response(
            {
                "campaigns_total": MarketingCampaign.objects.count(),
                "open_campaigns": open_count,
                "by_status": by_status,
                "by_channel": by_channel,
                "results_totals": {
                    "impressions": results.get("impressions") or 0,
                    "clicks": results.get("clicks") or 0,
                    "conversions": results.get("conversions") or 0,
                    "revenue_cents": results.get("revenue_cents") or 0,
                },
            }
        )


class CampaignResultListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = CampaignResultDailySerializer
    queryset = CampaignResultDaily.objects.select_related("campaign").all()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        campaign_id = request.query_params.get("campaign")
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        return success_response(self.get_serializer(qs[:200], many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)
