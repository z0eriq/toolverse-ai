from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.growth_agent")


@shared_task(name="apps.growth_agent.tasks.run_growth_agent_daily")
def run_growth_agent_daily() -> dict:
    from apps.growth_agent.services import run_growth_agent

    try:
        run = run_growth_agent()
        return {
            "run_id": run.pk,
            "status": run.status,
            "insights_created": run.insights_created,
            "error": run.error,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_growth_agent_daily failed")
        return {"error": str(exc)[:2000]}
