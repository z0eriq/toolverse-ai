from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.seo_optimizer")


@shared_task(name="apps.seo_optimizer.tasks.recompute_seo_health_daily")
def recompute_seo_health_daily() -> dict:
    from apps.seo_optimizer.health import recompute_all_seo_health

    try:
        return recompute_all_seo_health()
    except Exception as exc:  # noqa: BLE001
        logger.exception("recompute_seo_health_daily failed")
        return {"error": str(exc)[:2000]}


@shared_task(name="apps.seo_optimizer.tasks.generate_seo_opportunity_tasks_weekly")
def generate_seo_opportunity_tasks_weekly() -> dict:
    from apps.seo_optimizer.services import generate_seo_opportunity_tasks

    try:
        return generate_seo_opportunity_tasks()
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_seo_opportunity_tasks_weekly failed")
        return {"error": str(exc)[:2000]}


@shared_task(name="apps.seo_optimizer.tasks.run_seo_autopilot_daily")
def run_seo_autopilot_daily() -> dict:
    from apps.seo_optimizer.autopilot import scan_seo_autopilot

    try:
        run = scan_seo_autopilot()
        return {
            "id": run.pk,
            "status": run.status,
            "issues_created": run.issues_created,
            "error": run.error,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_seo_autopilot_daily failed")
        return {"error": str(exc)[:2000]}
