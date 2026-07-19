from __future__ import annotations

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.monetization.ad_services import generate_ad_recommendations
from apps.monetization.models import (
    AdOptimizationRec,
    AdPerformanceDaily,
    AdPlacement,
    AffiliateLink,
    RevenueEvent,
    SponsoredTool,
)
from apps.monetization.serializers import (
    AdOptimizationRecSerializer,
    AdPerformanceDailySerializer,
    AdPlacementSerializer,
    AffiliateLinkSerializer,
    RevenueEventSerializer,
    SponsoredToolSerializer,
)


class PublicPlacementsView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        qs = AdPlacement.objects.filter(enabled=True).order_by("key")
        return success_response(AdPlacementSerializer(qs, many=True).data)


class PublicAffiliatesView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        qs = AffiliateLink.objects.filter(is_active=True)
        tool_id = request.query_params.get("tool_id")
        if tool_id:
            qs = qs.filter(tool_id=tool_id)
        return success_response(AffiliateLinkSerializer(qs, many=True).data)


class PublicSponsoredView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        now = timezone.now()
        qs = SponsoredTool.objects.filter(is_active=True).select_related("tool")
        qs = qs.filter(models_q_start_end(now))
        return success_response(SponsoredToolSerializer(qs, many=True).data)


class AdSenseReadyView(APIView):
    """Public/admin readiness flag for AdSense client id + placements."""

    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        from apps.monetization.readiness import adsense_readiness

        return success_response(adsense_readiness())


def models_q_start_end(now):
    from django.db.models import Q

    return (Q(start_at__isnull=True) | Q(start_at__lte=now)) & (
        Q(end_at__isnull=True) | Q(end_at__gte=now)
    )


class AdminAdPlacementListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = AdPlacementSerializer
    queryset = AdPlacement.objects.all()

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class AdminAdPlacementDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = AdPlacementSerializer
    queryset = AdPlacement.objects.all()

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


class AdminSponsoredListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = SponsoredToolSerializer
    queryset = SponsoredTool.objects.select_related("tool").all()

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class AdminSponsoredDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = SponsoredToolSerializer
    queryset = SponsoredTool.objects.select_related("tool").all()

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


class AdminAffiliateListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = AffiliateLinkSerializer
    queryset = AffiliateLink.objects.select_related("tool").all()

    def list(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class AdminAffiliateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = AffiliateLinkSerializer
    queryset = AffiliateLink.objects.select_related("tool").all()

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


class AdminRevenueEventListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    serializer_class = RevenueEventSerializer
    queryset = RevenueEvent.objects.all()
    filterset_fields = ("type", "currency")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        return success_response(self.get_serializer(qs[:200], many=True).data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return success_response(self.get_serializer(obj).data, status_code=status.HTTP_201_CREATED)


class AdminRevenueSummaryView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        by_type = list(
            RevenueEvent.objects.values("type")
            .annotate(total_cents=Sum("amount_cents"), count=Count("id"))
            .order_by("type")
        )
        total = RevenueEvent.objects.aggregate(
            total_cents=Sum("amount_cents"),
            count=Count("id"),
        )
        return success_response(
            {
                "by_type": by_type,
                "total_cents": total.get("total_cents") or 0,
                "event_count": total.get("count") or 0,
                "placements": AdPlacement.objects.count(),
                "sponsored_active": SponsoredTool.objects.filter(is_active=True).count(),
                "affiliates_active": AffiliateLink.objects.filter(is_active=True).count(),
            }
        )


class AdminAdPerformanceListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = AdPerformanceDaily.objects.all().order_by("-date", "placement_key")
        key = request.query_params.get("placement_key")
        if key:
            qs = qs.filter(placement_key=key)
        return success_response(AdPerformanceDailySerializer(qs[:200], many=True).data)


class AdminAdRecommendationListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = AdOptimizationRec.objects.all().order_by("-priority", "-created_at")
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return success_response(AdOptimizationRecSerializer(qs[:200], many=True).data)

    def post(self, request):
        result = generate_ad_recommendations()
        qs = AdOptimizationRec.objects.filter(pk__in=result["ids"])
        return success_response(
            {
                "created": result["created"],
                "recommendations": AdOptimizationRecSerializer(qs, many=True).data,
            },
            status_code=status.HTTP_201_CREATED,
        )


class AdminAdRecommendationAcceptView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        from rest_framework.exceptions import NotFound

        try:
            rec = AdOptimizationRec.objects.get(pk=pk)
        except AdOptimizationRec.DoesNotExist as exc:
            raise NotFound("Recommendation not found") from exc
        rec.status = AdOptimizationRec.Status.ACCEPTED
        rec.save(update_fields=["status", "updated_at"])
        return success_response(AdOptimizationRecSerializer(rec).data)


class AdminAdRecommendationDismissView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        from rest_framework.exceptions import NotFound

        try:
            rec = AdOptimizationRec.objects.get(pk=pk)
        except AdOptimizationRec.DoesNotExist as exc:
            raise NotFound("Recommendation not found") from exc
        rec.status = AdOptimizationRec.Status.DISMISSED
        rec.save(update_fields=["status", "updated_at"])
        return success_response(AdOptimizationRecSerializer(rec).data)
