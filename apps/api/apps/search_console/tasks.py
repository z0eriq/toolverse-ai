from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.search_console")


@shared_task(name="apps.search_console.tasks.sync_gsc_daily")
def sync_gsc_daily() -> dict:
    from apps.search_console.services import sync_search_analytics

    try:
        return sync_search_analytics()
    except Exception as exc:  # noqa: BLE001
        logger.exception("sync_gsc_daily failed")
        return {"error": str(exc)[:2000]}
