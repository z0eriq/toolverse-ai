"""Conversion funnel aggregations for launch analytics."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count
from django.utils import timezone

from apps.analytics.models import AnalyticsEvent

# Event name aliases per funnel step
_IMPRESSION = ("page_view", "tool_impression", "impression", "view", "tool_view")
_CLICK = ("tool_click", "click")
_USE = ("tool_use", "use", "tool_run", "run", "tool_execution")
_COMPLETE = ("tool_complete", "complete")
_PREMIUM = ("premium_intent", "checkout_start", "upgrade_click")
_REVENUE = ("revenue", "purchase", "subscription_paid")


def _count_names(name_counts: dict[str, int], *aliases: str) -> int:
    return sum(name_counts.get(a, 0) for a in aliases)


def _completes_from_uses(events) -> int:
    """Count tool_complete events plus tool_use rows with action=complete."""
    named = events.filter(name__in=_COMPLETE).count()
    via_action = 0
    for props in events.filter(name__in=_USE).values_list("properties", flat=True):
        if isinstance(props, dict) and str(props.get("action", "")).lower() == "complete":
            via_action += 1
    return named + via_action


def _revenue_count(events, since) -> int:
    named = events.filter(name__in=_REVENUE).count()
    try:
        from apps.monetization.models import RevenueEvent

        named += RevenueEvent.objects.filter(created_at__gte=since).count()
    except Exception:  # noqa: BLE001
        pass
    return named


def build_conversion_funnel(*, days: int = 30) -> dict[str, Any]:
    """
    Build a conversion funnel for the last `days` window.

    Steps: impression → click → use → complete → premium_intent → revenue.
    Rates: completion_rate = completes/uses, conversion_rate = premium_or_paid/uses.
    """
    days = max(1, min(int(days or 30), 365))
    since = timezone.now() - timedelta(days=days)
    events = AnalyticsEvent.objects.filter(created_at__gte=since)

    name_counts = dict(
        events.values("name").annotate(c=Count("id")).values_list("name", "c")
    )

    impressions = _count_names(name_counts, *_IMPRESSION)
    clicks = _count_names(name_counts, *_CLICK)
    uses = _count_names(name_counts, *_USE)
    completes = _completes_from_uses(events)
    premium_intent = _count_names(name_counts, *_PREMIUM)
    revenue = _revenue_count(events, since)

    completion_rate = round(completes / uses, 4) if uses else 0.0
    # Conversion = premium intent or paid outcomes relative to uses
    converted = premium_intent + revenue
    conversion_rate = round(converted / uses, 4) if uses else 0.0

    steps = [
        {"key": "impression", "label": "Page view / tool impression", "count": impressions},
        {"key": "click", "label": "Tool click", "count": clicks},
        {"key": "use", "label": "Tool use", "count": uses},
        {"key": "complete", "label": "Tool complete", "count": completes},
        {"key": "premium_intent", "label": "Premium intent", "count": premium_intent},
        {"key": "revenue", "label": "Revenue", "count": revenue},
    ]

    return {
        "window_days": days,
        "steps": steps,
        "completion_rate": completion_rate,
        "conversion_rate": conversion_rate,
        "impressions": impressions,
        "clicks": clicks,
        "uses": uses,
        "completes": completes,
        "premium_intent": premium_intent,
        "revenue": revenue,
    }
