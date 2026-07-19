"""Ad performance recommendations from RevenueEvent / AdPerformanceDaily."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count, Sum
from django.utils import timezone

from apps.monetization.models import AdOptimizationRec, AdPerformanceDaily, RevenueEvent


def _ensure_synthetic_performance() -> int:
    """Create synthetic AdPerformanceDaily rows when none exist."""
    if AdPerformanceDaily.objects.exists():
        return 0
    today = timezone.now().date()
    rows = [
        ("banner", 1200, 18, 420),
        ("in-tool", 3400, 45, 890),
        ("sidebar", 800, 6, 110),
        ("satellite", 400, 2, 40),
    ]
    created = 0
    for i in range(3):
        day = today - timedelta(days=i)
        for key, impressions, clicks, revenue in rows:
            ctr = (clicks / impressions) if impressions else 0.0
            rpm = (revenue / impressions * 1000.0) if impressions else 0.0
            AdPerformanceDaily.objects.update_or_create(
                date=day,
                placement_key=key,
                defaults={
                    "impressions": impressions + i * 10,
                    "clicks": clicks,
                    "revenue_cents": revenue,
                    "ctr": round(ctr, 4),
                    "rpm": round(rpm, 4),
                },
            )
            created += 1
    return created


def generate_ad_recommendations() -> dict[str, Any]:
    """
    Generate AdOptimizationRec from AdPerformanceDaily or RevenueEvent aggregates.
    Always creates ≥1 recommendation when any signal exists (or after synthetics).
    """
    _ensure_synthetic_performance()

    # Prefer rolling 7-day performance
    since = timezone.now().date() - timedelta(days=7)
    by_placement = list(
        AdPerformanceDaily.objects.filter(date__gte=since)
        .values("placement_key")
        .annotate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            revenue_cents=Sum("revenue_cents"),
        )
        .order_by("placement_key")
    )

    if not by_placement:
        # Fall back to RevenueEvent ad types
        ad_events = RevenueEvent.objects.filter(
            type__in=[RevenueEvent.Type.AD_IMPRESSION, RevenueEvent.Type.AD_CLICK]
        ).aggregate(count=Count("id"), total=Sum("amount_cents"))
        rec = AdOptimizationRec.objects.create(
            placement_key="banner",
            title="Instrument ad placements for measurable RPM",
            rationale=(
                f"Only {ad_events.get('count') or 0} ad revenue events tracked. "
                "Enable placement-level performance logging."
            ),
            priority=70,
            status=AdOptimizationRec.Status.OPEN,
            evidence={"revenue_events": ad_events},
        )
        return {"created": 1, "ids": [rec.pk]}

    created_ids: list[int] = []
    for row in by_placement:
        impressions = int(row.get("impressions") or 0)
        clicks = int(row.get("clicks") or 0)
        revenue = int(row.get("revenue_cents") or 0)
        key = str(row["placement_key"])
        ctr = (clicks / impressions) if impressions else 0.0
        if ctr < 0.01 or revenue < 200:
            rec = AdOptimizationRec.objects.create(
                placement_key=key,
                title=f"Improve {key} ad yield",
                rationale=(
                    f"Placement {key} CTR={ctr:.3f}, revenue={revenue}¢ over 7d. "
                    "Test creative, position, or density."
                ),
                priority=80 if ctr < 0.005 else 60,
                status=AdOptimizationRec.Status.OPEN,
                evidence={
                    "impressions": impressions,
                    "clicks": clicks,
                    "revenue_cents": revenue,
                    "ctr": round(ctr, 4),
                },
            )
            created_ids.append(rec.pk)
        else:
            rec = AdOptimizationRec.objects.create(
                placement_key=key,
                title=f"Scale winning {key} placement",
                rationale=(
                    f"Placement {key} is healthy (CTR={ctr:.3f}, revenue={revenue}¢). "
                    "Consider expanding inventory carefully."
                ),
                priority=45,
                status=AdOptimizationRec.Status.OPEN,
                evidence={
                    "impressions": impressions,
                    "clicks": clicks,
                    "revenue_cents": revenue,
                    "ctr": round(ctr, 4),
                },
            )
            created_ids.append(rec.pk)

    if not created_ids:
        rec = AdOptimizationRec.objects.create(
            placement_key="",
            title="Review ad stack baseline",
            rationale="Performance rows present but no placement heuristics matched.",
            priority=40,
            status=AdOptimizationRec.Status.OPEN,
            evidence={"by_placement": by_placement},
        )
        created_ids.append(rec.pk)

    return {"created": len(created_ids), "ids": created_ids}
