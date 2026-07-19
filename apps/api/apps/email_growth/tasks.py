from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.email_growth")


@shared_task(name="apps.email_growth.tasks.send_weekly_digest")
def send_weekly_digest() -> dict:
    from apps.email_growth.services import send_weekly_digest as _send

    try:
        return _send()
    except Exception as exc:  # noqa: BLE001
        logger.exception("send_weekly_digest failed")
        return {"error": str(exc)[:2000]}
