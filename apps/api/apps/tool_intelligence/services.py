from __future__ import annotations

import logging
from typing import Any

from django.db.models import Sum
from django.utils.text import slugify

from apps.keywords.models import KeywordOpportunity
from apps.tool_intelligence.models import ToolOpportunity, ToolTemplate
from apps.tools_registry.discovery import CATEGORY_DEFAULTS
from apps.tools_registry.models import Tool

logger = logging.getLogger("toolverse.tool_intelligence")


def _category_keyword_impressions(category_slug: str) -> tuple[int, list[KeywordOpportunity]]:
    """Match keywords that mention category tokens or suggested tool slug prefix."""
    tokens = {category_slug.replace("-", " "), category_slug}
    qs = KeywordOpportunity.objects.all()
    matched: list[KeywordOpportunity] = []
    impressions = 0
    for kw in qs.iterator():
        hay = kw.keyword.lower()
        if any(t in hay for t in tokens) or (
            kw.suggested_tool_slug and category_slug in kw.suggested_tool_slug
        ):
            matched.append(kw)
            impressions += kw.impressions or kw.search_volume or 0
    if not matched:
        # Fallback: top keywords overall for demand signal
        top = list(KeywordOpportunity.objects.order_by("-impressions")[:5])
        impressions = sum(k.impressions or k.search_volume or 0 for k in top)
        matched = top
    return impressions, matched


def _scores_for_candidate(
    *,
    category_slug: str,
    priority_weight: float,
    existing_tool_count: int,
    impressions: int,
) -> dict[str, float]:
    demand = min(100.0, impressions / 10.0)
    competition = min(100.0, float(existing_tool_count) * 8.0)
    seo = max(0.0, min(100.0, demand * 0.7 + (100.0 - competition) * 0.3))
    value = max(0.0, (demand - competition * 0.4) * priority_weight)
    priority = round(seo * 0.35 + demand * 0.35 + value * 0.2 + (100 - competition) * 0.1, 4)
    return {
        "seo_score": round(seo, 4),
        "demand_score": round(demand, 4),
        "competition_score": round(competition, 4),
        "value_score": round(value, 4),
        "priority_score": priority,
    }


def recompute_tool_opportunities() -> dict[str, Any]:
    """
    For each CATEGORY_DEFAULTS entry and each ToolTemplate, compute opportunity
    scores from keyword impressions + existing tool counts, then upsert.
    """
    tool_counts: dict[str, int] = {}
    for slug in CATEGORY_DEFAULTS:
        tool_counts[slug] = Tool.objects.filter(category__slug=slug, is_active=True).count()

    created = updated = 0
    seen_slugs: set[str] = set()

    # Category-level gap opportunities
    for cat_slug, meta in CATEGORY_DEFAULTS.items():
        name_en = ""
        if isinstance(meta.get("name"), dict):
            name_en = str(meta["name"].get("en") or cat_slug)
        else:
            name_en = str(meta.get("name") or cat_slug)
        suggested = slugify(f"new-{cat_slug}-tool")[:120]
        impressions, matched = _category_keyword_impressions(cat_slug)
        scores = _scores_for_candidate(
            category_slug=cat_slug,
            priority_weight=1.0,
            existing_tool_count=tool_counts.get(cat_slug, 0),
            impressions=impressions,
        )
        defaults = {
            "category_slug": cat_slug,
            "title": f"Expand {name_en} tools",
            "rationale": (
                f"Category {cat_slug} has {tool_counts.get(cat_slug, 0)} tools and "
                f"{impressions} related keyword impressions."
            ),
            **scores,
        }
        obj, was_created = ToolOpportunity.objects.update_or_create(
            suggested_slug=suggested,
            defaults=defaults,
        )
        if matched:
            obj.keywords.set(matched[:20])
        seen_slugs.add(suggested)
        if was_created:
            created += 1
        else:
            updated += 1

    # Template-driven opportunities
    for tmpl in ToolTemplate.objects.all():
        suggested = tmpl.slug
        impressions, matched = _category_keyword_impressions(tmpl.category_slug)
        # Boost when keyword suggests this template slug
        kw_boost = KeywordOpportunity.objects.filter(
            suggested_tool_slug=tmpl.slug
        ).aggregate(total=Sum("impressions"))
        impressions += int(kw_boost.get("total") or 0)
        scores = _scores_for_candidate(
            category_slug=tmpl.category_slug,
            priority_weight=float(tmpl.priority_weight or 1.0),
            existing_tool_count=tool_counts.get(tmpl.category_slug, 0),
            impressions=impressions,
        )
        defaults = {
            "category_slug": tmpl.category_slug,
            "title": tmpl.slug.replace("-", " ").title(),
            "rationale": tmpl.description
            or f"Template {tmpl.slug} in {tmpl.category_slug} (recipe={tmpl.recipe}).",
            **scores,
        }
        obj, was_created = ToolOpportunity.objects.update_or_create(
            suggested_slug=suggested,
            defaults=defaults,
        )
        if matched:
            obj.keywords.set(matched[:20])
        seen_slugs.add(suggested)
        if was_created:
            created += 1
        else:
            updated += 1

    logger.info(
        "recompute_tool_opportunities created=%s updated=%s seen=%s",
        created,
        updated,
        len(seen_slugs),
    )
    return {"created": created, "updated": updated, "total": created + updated}


def queue_opportunity(opportunity: ToolOpportunity, *, user=None) -> ToolOpportunity:
    """Create a ToolSpec draft from the opportunity and mark it queued."""
    from apps.tool_factory.models import ToolSpec

    tmpl = ToolTemplate.objects.filter(slug=opportunity.suggested_slug).first()
    ui_schema = (tmpl.ui_schema if tmpl else {}) or {
        "fields": [{"name": "input", "type": "text", "label": "Input"}]
    }
    pipeline = (tmpl.pipeline if tmpl else []) or [
        {"type": "transform", "op": "identity", "input": "input", "output": "result"}
    ]
    recipe = (tmpl.recipe if tmpl else ToolSpec.Recipe.GENERIC) or ToolSpec.Recipe.GENERIC

    spec, _ = ToolSpec.objects.update_or_create(
        slug=opportunity.suggested_slug,
        defaults={
            "category_slug": opportunity.category_slug,
            "name": {"en": opportunity.title},
            "description": {"en": opportunity.rationale[:2000]},
            "ui_schema": ui_schema,
            "pipeline": pipeline,
            "recipe": recipe
            if recipe in {c.value for c in ToolSpec.Recipe}
            else ToolSpec.Recipe.GENERIC,
            "status": ToolSpec.Status.DRAFT,
            "created_by": user if getattr(user, "is_authenticated", False) else None,
        },
    )
    opportunity.tool_spec = spec
    opportunity.status = ToolOpportunity.Status.QUEUED
    opportunity.save(update_fields=["tool_spec", "status", "updated_at"])
    return opportunity


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 4)


def recompute_tool_performance_scores() -> dict[str, Any]:
    """
    Deterministic live scores for each active Tool.
    Components (0–100): traffic, usage, revenue, seo, retention → priority_score.
    """
    from datetime import timedelta

    from django.db.models import Count, Sum
    from django.utils import timezone

    from apps.tool_intelligence.models import ToolPerformanceScore
    from apps.tools_registry.models import Tool

    now = timezone.now()
    since = now - timedelta(days=30)
    tools = list(Tool.objects.filter(is_active=True))
    if not tools:
        return {"updated": 0, "total": 0}

    # Usage / traffic from analytics
    usage_by_tool: dict[str, int] = {}
    traffic_by_tool: dict[str, int] = {}
    retention_by_tool: dict[str, float] = {}
    try:
        from apps.analytics.models import AnalyticsEvent

        usage_rows = (
            AnalyticsEvent.objects.filter(
                created_at__gte=since,
                name__in=("use", "tool_use", "tool_run", "run", "tool_execution"),
            )
            .exclude(tool_id="")
            .values("tool_id")
            .annotate(c=Count("id"))
        )
        usage_by_tool = {r["tool_id"]: r["c"] for r in usage_rows}

        traffic_rows = (
            AnalyticsEvent.objects.filter(created_at__gte=since)
            .exclude(tool_id="")
            .values("tool_id")
            .annotate(c=Count("id"))
        )
        traffic_by_tool = {r["tool_id"]: r["c"] for r in traffic_rows}

        from django.db.models.functions import TruncDate

        # Retention proxy: share of tool actors active on 2+ distinct days
        for tool in tools:
            tid = tool.tool_id
            actor_days: dict[str, set] = {}
            for row in (
                AnalyticsEvent.objects.filter(created_at__gte=since, tool_id=tid)
                .annotate(day=TruncDate("created_at"))
                .values("session_id", "user_id", "day")[:5000]
            ):
                actor = row["session_id"] or (
                    f"u:{row['user_id']}" if row["user_id"] else ""
                )
                if not actor:
                    continue
                actor_days.setdefault(actor, set()).add(row["day"])
            total = len(actor_days)
            returning = sum(1 for d in actor_days.values() if len(d) >= 2)
            retention_by_tool[tid] = (returning / total * 100.0) if total else 0.0
    except Exception as exc:  # noqa: BLE001
        logger.debug("analytics scores skipped: %s", exc)

    # GSC impressions by page containing tool slug
    gsc_by_slug: dict[str, int] = {}
    try:
        from apps.search_console.models import GSCMetricSnapshot

        for snap in GSCMetricSnapshot.objects.filter(date__gte=since.date()).iterator():
            page = (snap.page or "").lower()
            for tool in tools:
                if tool.slug and tool.slug in page:
                    gsc_by_slug[tool.tool_id] = gsc_by_slug.get(tool.tool_id, 0) + int(
                        snap.impressions or 0
                    )
    except Exception as exc:  # noqa: BLE001
        logger.debug("gsc scores skipped: %s", exc)

    # SEO health for tool paths
    seo_by_slug: dict[str, float] = {}
    try:
        from apps.seo_optimizer.models import SeoHealthScore

        for hs in SeoHealthScore.objects.all().iterator():
            path = (hs.path or "").lower()
            for tool in tools:
                if tool.slug and tool.slug in path:
                    seo_by_slug[tool.tool_id] = float(hs.overall or 0.0)
    except Exception as exc:  # noqa: BLE001
        logger.debug("seo scores skipped: %s", exc)

    # Revenue attributed by tool_id in meta
    revenue_by_tool: dict[str, int] = {}
    try:
        from apps.monetization.models import RevenueEvent

        for ev in RevenueEvent.objects.filter(created_at__gte=since).iterator():
            meta = ev.meta if isinstance(ev.meta, dict) else {}
            tid = str(meta.get("tool_id") or meta.get("tool") or "")
            if tid:
                revenue_by_tool[tid] = revenue_by_tool.get(tid, 0) + int(
                    ev.amount_cents or 0
                )
    except Exception as exc:  # noqa: BLE001
        logger.debug("revenue scores skipped: %s", exc)

    max_usage = max(usage_by_tool.values(), default=0) or 1
    max_traffic = max(
        (traffic_by_tool.get(t.tool_id, 0) + gsc_by_slug.get(t.tool_id, 0) for t in tools),
        default=0,
    ) or 1
    max_revenue = max(revenue_by_tool.values(), default=0) or 1
    max_usage_count = max((t.usage_count for t in tools), default=0) or 1

    updated = 0
    for tool in tools:
        tid = tool.tool_id
        raw_traffic = traffic_by_tool.get(tid, 0) + gsc_by_slug.get(tid, 0)
        traffic_score = _clamp_score((raw_traffic / max_traffic) * 100.0)
        usage_raw = usage_by_tool.get(tid, 0) + (
            tool.usage_count / max_usage_count * max_usage * 0.25
        )
        usage_score = _clamp_score((usage_raw / max(max_usage, 1)) * 100.0)
        revenue_score = _clamp_score(
            (revenue_by_tool.get(tid, 0) / max_revenue) * 100.0
        )
        seo_score = _clamp_score(seo_by_slug.get(tid, 50.0))
        retention_score = _clamp_score(retention_by_tool.get(tid, 0.0))
        priority_score = _clamp_score(
            traffic_score * 0.2
            + usage_score * 0.25
            + revenue_score * 0.2
            + seo_score * 0.2
            + retention_score * 0.15
        )
        ToolPerformanceScore.objects.update_or_create(
            tool=tool,
            defaults={
                "traffic_score": traffic_score,
                "usage_score": usage_score,
                "revenue_score": revenue_score,
                "seo_score": seo_score,
                "retention_score": retention_score,
                "priority_score": priority_score,
                "computed_at": now,
            },
        )
        updated += 1

    logger.info("recompute_tool_performance_scores updated=%s", updated)
    return {"updated": updated, "total": updated}
