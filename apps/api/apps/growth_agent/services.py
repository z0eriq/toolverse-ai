from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.db.models import Avg, Sum
from django.utils import timezone

from apps.growth_agent.models import GrowthAgentRun, GrowthInsight, GrowthTask

logger = logging.getLogger("toolverse.growth_agent")


def _snapshot() -> dict[str, Any]:
    data: dict[str, Any] = {
        "analytics_events_7d": 0,
        "keyword_top": [],
        "opportunities_open": 0,
        "seo_health_avg": None,
        "revenue_cents": 0,
        "pending_reviews": 0,
        "pending_comments": 0,
    }

    try:
        from datetime import timedelta

        from apps.analytics.models import AnalyticsEvent

        since = timezone.now() - timedelta(days=7)
        data["analytics_events_7d"] = AnalyticsEvent.objects.filter(created_at__gte=since).count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("analytics snapshot skipped: %s", exc)

    try:
        from apps.keywords.models import KeywordOpportunity

        data["keyword_top"] = list(
            KeywordOpportunity.objects.order_by("-priority_score").values(
                "keyword", "priority_score", "impressions"
            )[:5]
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("keywords snapshot skipped: %s", exc)

    try:
        from apps.tool_intelligence.models import ToolOpportunity

        data["opportunities_open"] = ToolOpportunity.objects.filter(
            status=ToolOpportunity.Status.OPEN
        ).count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("opportunities snapshot skipped: %s", exc)

    try:
        from apps.seo_optimizer.models import SeoHealthScore

        avg = SeoHealthScore.objects.aggregate(avg=Avg("overall")).get("avg")
        data["seo_health_avg"] = float(avg) if avg is not None else None
        data["seo_health_count"] = SeoHealthScore.objects.count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("seo health snapshot skipped: %s", exc)

    try:
        from apps.monetization.models import RevenueEvent

        agg = RevenueEvent.objects.aggregate(total=Sum("amount_cents"))
        data["revenue_cents"] = int(agg.get("total") or 0)
    except Exception as exc:  # noqa: BLE001
        logger.debug("revenue snapshot skipped: %s", exc)

    try:
        from apps.engagement.models import ToolComment, ToolReview

        data["pending_reviews"] = ToolReview.objects.filter(
            status=ToolReview.Status.PENDING
        ).count()
        data["pending_comments"] = ToolComment.objects.filter(
            status=ToolComment.Status.PENDING
        ).count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("engagement snapshot skipped: %s", exc)

    return data


def _build_insights(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []

    events = int(snapshot.get("analytics_events_7d") or 0)
    if events < 100:
        insights.append(
            {
                "category": GrowthInsight.Category.TRAFFIC,
                "title": "Grow top-of-funnel traffic",
                "rationale": (
                    f"Only {events} analytics events in the last 7 days. "
                    "Prioritize programmatic SEO pages and newsletter acquisition."
                ),
                "priority": 80 if events < 20 else 60,
                "meta": {"analytics_events_7d": events},
            }
        )
    else:
        insights.append(
            {
                "category": GrowthInsight.Category.TRAFFIC,
                "title": "Double down on converting traffic",
                "rationale": (
                    f"{events} events in 7 days — focus on tool CTAs and email capture "
                    "on high-traffic paths."
                ),
                "priority": 55,
                "meta": {"analytics_events_7d": events},
            }
        )

    seo_avg = snapshot.get("seo_health_avg")
    if seo_avg is None:
        insights.append(
            {
                "category": GrowthInsight.Category.SEO,
                "title": "Run SEO health scoring",
                "rationale": "No SeoHealthScore rows yet. Recompute health for published pages and top tools.",
                "priority": 70,
                "meta": {},
            }
        )
    elif seo_avg < 70:
        insights.append(
            {
                "category": GrowthInsight.Category.SEO,
                "title": "Lift average SEO health above 70",
                "rationale": f"Average SEO health is {seo_avg:.1f}. Fix metadata, FAQ schema, and internal links.",
                "priority": 75,
                "meta": {"seo_health_avg": seo_avg},
            }
        )
    else:
        insights.append(
            {
                "category": GrowthInsight.Category.SEO,
                "title": "Maintain strong SEO health",
                "rationale": f"Average SEO health is {seo_avg:.1f}. Keep monitoring underperforming paths.",
                "priority": 40,
                "meta": {"seo_health_avg": seo_avg},
            }
        )

    open_ops = int(snapshot.get("opportunities_open") or 0)
    keywords = snapshot.get("keyword_top") or []
    if open_ops > 0:
        insights.append(
            {
                "category": GrowthInsight.Category.TOOLS,
                "title": f"Ship {min(open_ops, 5)} open tool opportunities",
                "rationale": f"{open_ops} open ToolOpportunity rows — queue the highest priority_score items.",
                "priority": 85,
                "meta": {"opportunities_open": open_ops},
            }
        )
    elif keywords:
        top = keywords[0]
        insights.append(
            {
                "category": GrowthInsight.Category.CONTENT,
                "title": f"Create content for “{top.get('keyword')}”",
                "rationale": "Top keyword opportunity has no matching open tool — consider a programmatic page.",
                "priority": 65,
                "meta": {"keyword": top},
            }
        )
    else:
        insights.append(
            {
                "category": GrowthInsight.Category.TOOLS,
                "title": "Seed keyword and opportunity pipelines",
                "rationale": "No keyword opportunities or tool opportunities found. Sync GSC and recompute.",
                "priority": 50,
                "meta": {},
            }
        )

    revenue = int(snapshot.get("revenue_cents") or 0)
    if revenue <= 0:
        insights.append(
            {
                "category": GrowthInsight.Category.REVENUE,
                "title": "Enable monetization instrumentation",
                "rationale": "No RevenueEvent rows yet. Verify ad placements and subscription checkout tracking.",
                "priority": 58,
                "meta": {"revenue_cents": revenue},
            }
        )
    else:
        insights.append(
            {
                "category": GrowthInsight.Category.REVENUE,
                "title": "Optimize high-yield revenue surfaces",
                "rationale": f"Tracked revenue events total {revenue} cents. Review sponsored tools and API usage.",
                "priority": 52,
                "meta": {"revenue_cents": revenue},
            }
        )

    pending_reviews = int(snapshot.get("pending_reviews") or 0)
    pending_comments = int(snapshot.get("pending_comments") or 0)
    if pending_reviews or pending_comments:
        insights.append(
            {
                "category": GrowthInsight.Category.CONTENT,
                "title": "Moderate pending community feedback",
                "rationale": (
                    f"{pending_reviews} pending reviews and {pending_comments} pending comments "
                    "await moderation — clear the queue to improve trust signals."
                ),
                "priority": 72 if pending_reviews + pending_comments > 5 else 55,
                "meta": {
                    "pending_reviews": pending_reviews,
                    "pending_comments": pending_comments,
                },
            }
        )

    # Always at least one
    if not insights:
        insights.append(
            {
                "category": GrowthInsight.Category.CONTENT,
                "title": "Establish baseline growth loop",
                "rationale": "Empty data snapshot — start with SEO health recompute and keyword sync.",
                "priority": 50,
                "meta": {},
            }
        )

    return insights


@transaction.atomic
def run_growth_agent() -> GrowthAgentRun:
    """Deterministic growth insights from analytics / keywords / SEO / revenue."""
    run = GrowthAgentRun.objects.create(status=GrowthAgentRun.Status.RUNNING)
    try:
        snapshot = _snapshot()
        payloads = _build_insights(snapshot)
        created = 0
        for item in payloads:
            insight = GrowthInsight.objects.create(
                category=item["category"],
                title=item["title"],
                rationale=item.get("rationale") or "",
                priority=int(item.get("priority") or 50),
                status=GrowthInsight.Status.OPEN,
                meta=item.get("meta") or {},
                source_snapshot=snapshot,
            )
            GrowthTask.objects.create(
                title=item["title"],
                category=item["category"],
                priority=int(item.get("priority") or 50),
                status=GrowthTask.Status.OPEN,
                insight=insight,
                meta=item.get("meta") or {},
            )
            created += 1

        from apps.growth_agent.actions import propose_growth_actions

        actions = propose_growth_actions(run)
        run.status = GrowthAgentRun.Status.SUCCESS
        run.insights_created = created
        run.summary = (
            f"Created {created} insights and {len(actions)} proposed growth actions."
        )
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "status",
                "insights_created",
                "summary",
                "finished_at",
                "updated_at",
            ]
        )
        return run
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_growth_agent failed")
        run.status = GrowthAgentRun.Status.FAILED
        run.error = str(exc)[:2000]
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at", "updated_at"])
        # Guarantee ≥1 insight even on failure path with empty DB edge cases
        if not GrowthInsight.objects.filter(
            created_at__gte=run.created_at
        ).exists():
            GrowthInsight.objects.create(
                category=GrowthInsight.Category.CONTENT,
                title="Growth agent recovered with fallback insight",
                rationale="Primary run failed; review error on GrowthAgentRun and retry.",
                priority=40,
                meta={"run_id": run.pk},
                source_snapshot={},
            )
            insight = GrowthInsight.objects.filter(
                title="Growth agent recovered with fallback insight",
                meta__run_id=run.pk,
            ).first()
            if insight:
                GrowthTask.objects.create(
                    title=insight.title,
                    category=insight.category,
                    priority=insight.priority,
                    status=GrowthTask.Status.OPEN,
                    insight=insight,
                    meta=insight.meta or {},
                )
            run.insights_created = 1
            run.save(update_fields=["insights_created", "updated_at"])
        try:
            from apps.growth_agent.actions import propose_growth_actions

            propose_growth_actions(run)
        except Exception:  # noqa: BLE001
            logger.debug("propose_growth_actions after failure skipped", exc_info=True)
        return run
