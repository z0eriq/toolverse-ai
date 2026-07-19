from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.tool_intelligence")


@shared_task(name="apps.tool_intelligence.tasks.recompute_tool_opportunities_daily")
def recompute_tool_opportunities_daily() -> dict:
    from apps.tool_intelligence.services import recompute_tool_opportunities

    try:
        return recompute_tool_opportunities()
    except Exception as exc:  # noqa: BLE001
        logger.exception("recompute_tool_opportunities_daily failed")
        return {"error": str(exc)[:2000]}


@shared_task(name="apps.tool_intelligence.tasks.recompute_tool_scores_daily")
def recompute_tool_scores_daily() -> dict:
    from apps.tool_intelligence.services import recompute_tool_performance_scores

    try:
        return recompute_tool_performance_scores()
    except Exception as exc:  # noqa: BLE001
        logger.exception("recompute_tool_scores_daily failed")
        return {"error": str(exc)[:2000]}
