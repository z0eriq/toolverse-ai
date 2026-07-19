"""Competitor gap analysis."""

from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.competitor_intel.models import CompetitorDomain, CompetitorKeyword, CompetitorOpportunity


@transaction.atomic
def recompute_competitor_opportunities() -> dict[str, Any]:
    """
    Create CompetitorOpportunity rows for keywords competitors rank for
    that we do not cover (our_has_coverage=False).
    """
    created = 0
    for kw in CompetitorKeyword.objects.filter(our_has_coverage=False).select_related(
        "competitor"
    ):
        gap = float(kw.search_volume) * max(0.1, (21.0 - min(kw.position, 20.0)) / 20.0)
        title = f"Capture “{kw.keyword}” vs {kw.competitor.domain}"
        obj, was_created = CompetitorOpportunity.objects.update_or_create(
            competitor=kw.competitor,
            keyword=kw.keyword,
            defaults={
                "title": title[:255],
                "rationale": (
                    f"{kw.competitor.domain} ranks ~{kw.position:.0f} for “{kw.keyword}” "
                    f"(vol={kw.search_volume}) and we lack coverage."
                ),
                "gap_score": round(gap, 2),
                "status": CompetitorOpportunity.Status.OPEN,
                "evidence": {
                    "position": kw.position,
                    "search_volume": kw.search_volume,
                    "keyword_id": kw.pk,
                },
            },
        )
        if was_created:
            created += 1
    return {"created": created, "open": CompetitorOpportunity.objects.filter(status="open").count()}
