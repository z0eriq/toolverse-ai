from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("toolverse.marketplace")


@shared_task(name="apps.marketplace.tasks.generate_invoices_from_usage_monthly")
def generate_invoices_from_usage_monthly() -> dict:
    from apps.marketplace.billing import generate_invoices_from_usage

    try:
        return generate_invoices_from_usage()
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_invoices_from_usage_monthly failed")
        return {"error": str(exc)[:2000]}
