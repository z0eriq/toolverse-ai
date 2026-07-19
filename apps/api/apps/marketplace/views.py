from __future__ import annotations

import logging
from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.audit import log_audit
from apps.common.exceptions import success_response
from apps.marketplace.models import ApiInvoiceStub, ApiKey, ApiUsage, DeveloperOrganization, SalesLead
from apps.marketplace.serializers import (
    ApiInvoiceStubSerializer,
    ApiKeyCreateSerializer,
    ApiKeySerializer,
    DeveloperOrganizationCreateSerializer,
    DeveloperOrganizationSerializer,
    SalesLeadCreateSerializer,
    SalesLeadSerializer,
)

logger = logging.getLogger("toolverse.marketplace")


class ApiKeyListCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        keys = ApiKey.objects.filter(user=request.user).order_by("-created_at")
        return success_response(ApiKeySerializer(keys, many=True).data)

    def post(self, request):
        serializer = ApiKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        key, plaintext = ApiKey.create_for_user(
            request.user,
            name=data["name"],
            scopes=data.get("scopes") or [],
            rate_limit_per_minute=data.get("rate_limit_per_minute", 60),
            monthly_quota=data.get("monthly_quota", 10_000),
        )
        log_audit(
            request,
            "marketplace.api_key.create",
            resource_type="marketplace.ApiKey",
            resource_id=key.pk,
            meta={"name": key.name, "key_prefix": key.key_prefix},
        )
        payload = ApiKeySerializer(key).data
        payload["key"] = plaintext  # shown once
        return success_response(payload, status_code=status.HTTP_201_CREATED)


class ApiKeyRevokeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk: int):
        try:
            key = ApiKey.objects.get(pk=pk, user=request.user)
        except ApiKey.DoesNotExist as exc:
            raise NotFound("API key not found") from exc
        key.revoke()
        log_audit(
            request,
            "marketplace.api_key.revoke",
            resource_type="marketplace.ApiKey",
            resource_id=key.pk,
            meta={"name": key.name, "key_prefix": key.key_prefix},
        )
        return success_response(ApiKeySerializer(key).data)


class ApiUsageSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        keys = ApiKey.objects.filter(user=request.user)
        active = keys.filter(revoked_at__isnull=True).count()
        revoked = keys.filter(revoked_at__isnull=False).count()
        usage_agg = ApiUsage.objects.filter(api_key__user=request.user).aggregate(
            total_units=Sum("units"),
            total_calls=Count("id"),
        )
        by_endpoint = list(
            ApiUsage.objects.filter(api_key__user=request.user)
            .values("endpoint")
            .annotate(calls=Count("id"), units=Sum("units"))
            .order_by("-calls")[:20]
        )
        return success_response(
            {
                "keys_total": keys.count(),
                "keys_active": active,
                "keys_revoked": revoked,
                "usage_this_month": sum(keys.values_list("usage_this_month", flat=True)),
                "total_units": usage_agg["total_units"] or 0,
                "total_calls": usage_agg["total_calls"] or 0,
                "by_endpoint": by_endpoint,
            }
        )


class MarketplaceAnalyticsView(APIView):
    """Daily usage for the authenticated user's API keys."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        days = min(int(request.query_params.get("days") or 30), 90)
        since = timezone.now() - timedelta(days=days)
        daily = list(
            ApiUsage.objects.filter(api_key__user=request.user, created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(calls=Count("id"), units=Sum("units"))
            .order_by("day")
        )
        by_key = list(
            ApiUsage.objects.filter(api_key__user=request.user, created_at__gte=since)
            .values("api_key_id", "api_key__key_prefix", "api_key__name")
            .annotate(calls=Count("id"), units=Sum("units"))
            .order_by("-calls")[:50]
        )
        return success_response({"days": days, "daily": daily, "by_key": by_key})


class DeveloperOrgListCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = DeveloperOrganization.objects.filter(owner=request.user).order_by("name")
        return success_response(DeveloperOrganizationSerializer(qs, many=True).data)

    def post(self, request):
        ser = DeveloperOrganizationCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        org = DeveloperOrganization.objects.create(
            name=ser.validated_data["name"],
            owner=request.user,
            plan_tier=ser.validated_data.get("plan_tier")
            or DeveloperOrganization.PlanTier.FREE,
        )
        return success_response(
            DeveloperOrganizationSerializer(org).data,
            status_code=status.HTTP_201_CREATED,
        )


class AdminInvoiceListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = ApiInvoiceStub.objects.select_related("org").order_by("-period_end")[:200]
        return success_response(ApiInvoiceStubSerializer(qs, many=True).data)


class StripeMeterWebhookView(APIView):
    """Stub webhook — logs payload only; wire Stripe signature verification later."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        event_type = request.data.get("type") if isinstance(request.data, dict) else None
        logger.info(
            "Stripe meter webhook received type=%s keys=%s",
            event_type,
            list(request.data.keys()) if isinstance(request.data, dict) else type(request.data),
        )
        return success_response({"received": True})


class SalesLeadCreateView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = []  # use default anon throttle from REST_FRAMEWORK
    authentication_classes: list = []

    def get_throttles(self):
        from rest_framework.throttling import AnonRateThrottle

        return [AnonRateThrottle()]

    def post(self, request):
        ser = SalesLeadCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        meta = dict(data.get("meta") or {})
        # Copy UTM from meta when top-level missing
        for field in ("utm_source", "utm_medium", "utm_campaign", "campaign_key"):
            if not data.get(field) and meta.get(field):
                data[field] = str(meta.get(field))[:128]
        lead = SalesLead.objects.create(
            name=data["name"],
            email=data["email"],
            company=data.get("company") or "",
            company_size=data.get("company_size") or "",
            role=data.get("role") or "",
            message=data.get("message") or "",
            intent=data.get("intent") or SalesLead.Intent.CONTACT,
            utm_source=data.get("utm_source") or "",
            utm_medium=data.get("utm_medium") or "",
            utm_campaign=data.get("utm_campaign") or "",
            campaign_key=data.get("campaign_key") or "",
            meta=meta,
            status=SalesLead.Status.NEW,
        )
        return success_response(
            SalesLeadSerializer(lead).data,
            status_code=status.HTTP_201_CREATED,
        )


class AdminSalesLeadListView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = SalesLead.objects.all().order_by("-created_at")
        status_filter = request.query_params.get("status")
        intent = request.query_params.get("intent")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if intent:
            qs = qs.filter(intent=intent)
        return success_response(SalesLeadSerializer(qs[:200], many=True).data)
