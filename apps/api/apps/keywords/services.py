from __future__ import annotations

import logging
import re
from typing import Any

from django.db.models import Avg, Sum
from django.utils import timezone
from django.utils.text import slugify

from apps.keywords.models import KeywordOpportunity

logger = logging.getLogger("toolverse.keywords")


def difficulty_from_position(position: float | None) -> int:
    """Heuristic SEO difficulty from average SERP position (0–100)."""
    if position is None or position <= 0:
        return 50
    # Lower rank → easier to hold; deep positions → harder opportunity
    if position <= 3:
        return 15
    if position <= 10:
        return 35
    if position <= 20:
        return 55
    if position <= 40:
        return 70
    return min(100, int(40 + position))


def priority_from_metrics(
    impressions: int,
    clicks: int,
    ctr: float,
    difficulty: int,
) -> float:
    volume = max(impressions, clicks * 10)
    return round((volume * (ctr + 0.01)) / (difficulty + 1), 4)


def suggested_slug_for_keyword(keyword: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", keyword.lower())
    return slugify(cleaned)[:120] or "keyword-opportunity"


def upsert_keywords_from_gsc(*, locale: str = "en") -> dict[str, Any]:
    """
    Aggregate GSCMetricSnapshot by query and upsert KeywordOpportunity rows.
    search_volume is derived from impressions; difficulty from avg position.
    """
    from apps.search_console.models import GSCMetricSnapshot

    rows = (
        GSCMetricSnapshot.objects.exclude(query="")
        .values("query")
        .annotate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_ctr=Avg("ctr"),
            avg_position=Avg("position"),
        )
        .order_by("-impressions")
    )

    now = timezone.now()
    created = updated = 0
    for row in rows:
        keyword = str(row["query"] or "").strip()[:512]
        if not keyword:
            continue
        impressions = int(row.get("impressions") or 0)
        clicks = int(row.get("clicks") or 0)
        ctr = float(row.get("avg_ctr") or 0.0)
        position = row.get("avg_position")
        ranking = float(position) if position is not None else None
        difficulty = difficulty_from_position(ranking)
        priority = priority_from_metrics(impressions, clicks, ctr, difficulty)
        defaults = {
            "search_volume": impressions,
            "difficulty": difficulty,
            "ranking_position": ranking,
            "ctr": ctr,
            "clicks": clicks,
            "impressions": impressions,
            "suggested_tool_slug": suggested_slug_for_keyword(keyword),
            "priority_score": priority,
            "last_synced_at": now,
        }
        _, was_created = KeywordOpportunity.objects.update_or_create(
            keyword=keyword,
            locale=locale,
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    logger.info("upsert_keywords_from_gsc created=%s updated=%s", created, updated)
    return {"created": created, "updated": updated, "total": created + updated}
