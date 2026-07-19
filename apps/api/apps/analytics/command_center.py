"""Launch Command Center aggregations for admin executive dashboard."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from apps.analytics.models import AnalyticsEvent

User = get_user_model()


def build_command_center(*, days: int = 30) -> dict[str, Any]:
    """Aggregate executive KPIs for the last `days` window."""
    days = max(1, min(int(days or 30), 365))
    now = timezone.now()
    since = now - timedelta(days=days)
    mau_since = now - timedelta(days=30)
    dau_since = now - timedelta(days=1)

    events = AnalyticsEvent.objects.filter(created_at__gte=since)

    dau = (
        AnalyticsEvent.objects.filter(created_at__gte=dau_since)
        .exclude(user_id=None)
        .values("user_id")
        .distinct()
        .count()
    )
    # Fall back to session-based DAU when users are sparse
    if dau == 0:
        dau = (
            AnalyticsEvent.objects.filter(created_at__gte=dau_since)
            .exclude(session_id="")
            .values("session_id")
            .distinct()
            .count()
        )

    mau = (
        AnalyticsEvent.objects.filter(created_at__gte=mau_since)
        .exclude(user_id=None)
        .values("user_id")
        .distinct()
        .count()
    )
    if mau == 0:
        mau = (
            AnalyticsEvent.objects.filter(created_at__gte=mau_since)
            .exclude(session_id="")
            .values("session_id")
            .distinct()
            .count()
        )

    registrations = User.objects.filter(date_joined__gte=since).count()

    tool_executions = events.filter(
        name__in=("use", "tool_use", "tool_run", "run", "tool_execution")
    ).count()

    premium_conversions = 0
    try:
        from apps.subscriptions.models import Subscription

        premium_conversions = Subscription.objects.filter(
            created_at__gte=since,
            plan__slug__in=("premium", "pro"),
        ).count()
    except Exception:  # noqa: BLE001
        premium_conversions = 0

    revenue_cents = 0
    try:
        from apps.monetization.models import RevenueEvent

        revenue_cents = int(
            RevenueEvent.objects.filter(created_at__gte=since).aggregate(
                total=Sum("amount_cents")
            )["total"]
            or 0
        )
    except Exception:  # noqa: BLE001
        revenue_cents = 0

    api_usage_units = 0
    try:
        from apps.marketplace.models import ApiUsage

        api_usage_units = int(
            ApiUsage.objects.filter(created_at__gte=since).aggregate(total=Sum("units"))[
                "total"
            ]
            or 0
        )
    except Exception:  # noqa: BLE001
        api_usage_units = 0

    seo_clicks = 0
    seo_impressions = 0
    try:
        from apps.search_console.models import GSCMetricSnapshot

        gsc = GSCMetricSnapshot.objects.filter(date__gte=since.date()).aggregate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
        )
        seo_clicks = int(gsc.get("clicks") or 0)
        seo_impressions = int(gsc.get("impressions") or 0)
    except Exception:  # noqa: BLE001
        seo_clicks = 0
        seo_impressions = 0

    countries = list(
        events.exclude(country="")
        .values("country")
        .annotate(count=Count("id"))
        .order_by("-count")[:15]
    )
    top_tools = list(
        events.exclude(tool_id="")
        .values("tool_id")
        .annotate(count=Count("id"))
        .order_by("-count")[:15]
    )

    funnel_snapshot: dict[str, Any] = {}
    try:
        from apps.analytics.funnels import build_conversion_funnel

        funnel_snapshot = build_conversion_funnel(days=days)
    except Exception:  # noqa: BLE001
        funnel_snapshot = {}

    adsense_ready = False
    try:
        from apps.monetization.readiness import adsense_readiness

        adsense_ready = bool(adsense_readiness().get("adsense_ready"))
    except Exception:  # noqa: BLE001
        adsense_ready = False

    deploy_release = (
        getattr(settings, "DEPLOY_RELEASE", "")
        or getattr(settings, "SENTRY_RELEASE", "")
        or ""
    )

    open_campaigns = 0
    try:
        from apps.campaigns.models import MarketingCampaign

        open_campaigns = MarketingCampaign.objects.filter(
            status__in=(
                MarketingCampaign.Status.ACTIVE,
                MarketingCampaign.Status.DRAFT,
            )
        ).count()
    except Exception:  # noqa: BLE001
        open_campaigns = 0

    indexed_urls_count = 0
    try:
        from apps.search_console.models import IndexedUrl

        indexed_urls_count = IndexedUrl.objects.count()
    except Exception:  # noqa: BLE001
        indexed_urls_count = 0

    draft_tool_specs_count = 0
    try:
        from apps.tool_factory.models import ToolSpec

        draft_tool_specs_count = ToolSpec.objects.filter(
            status=ToolSpec.Status.DRAFT
        ).count()
    except Exception:  # noqa: BLE001
        draft_tool_specs_count = 0

    return {
        "window_days": days,
        "dau": int(dau),
        "mau": int(mau),
        "registrations": int(registrations),
        "tool_executions": int(tool_executions),
        "premium_conversions": int(premium_conversions),
        "revenue_cents": int(revenue_cents),
        "api_usage_units": int(api_usage_units),
        "seo_clicks": int(seo_clicks),
        "seo_impressions": int(seo_impressions),
        "countries": countries,
        "top_tools": top_tools,
        "funnel": funnel_snapshot,
        "adsense_ready": adsense_ready,
        "deploy_release": deploy_release,
        "open_campaigns": int(open_campaigns),
        "indexed_urls_count": int(indexed_urls_count),
        "draft_tool_specs_count": int(draft_tool_specs_count),
    }
