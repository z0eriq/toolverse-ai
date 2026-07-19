from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.keywords")


@shared_task(name="apps.keywords.tasks.recompute_keywords_from_gsc")
def recompute_keywords_from_gsc() -> dict:
    from apps.keywords.services import upsert_keywords_from_gsc

    try:
        return upsert_keywords_from_gsc()
    except Exception as exc:  # noqa: BLE001
        logger.exception("recompute_keywords_from_gsc failed")
        return {"error": str(exc)[:2000]}
