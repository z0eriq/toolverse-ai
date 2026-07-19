from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger("toolverse.health")


def _release() -> str:
    return (
        os.getenv("APP_RELEASE")
        or getattr(settings, "APP_RELEASE", "")
        or "local"
    )


def healthz(_request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "toolverse-api",
            "release": _release(),
        }
    )


def _check_celery_broker() -> str:
    """Ping Celery broker (Redis) when configured."""
    broker = getattr(settings, "CELERY_BROKER_URL", "") or ""
    if not broker:
        return "skipped"
    try:
        import redis

        client = redis.from_url(broker)
        client.ping()
        return "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Celery broker check failed: %s", exc)
        return f"error: {exc}"


def readyz(_request):
    checks: dict[str, str] = {}
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc}"

    try:
        cache.set("readyz", "1", 5)
        checks["cache"] = "ok" if cache.get("readyz") == "1" else "error"
    except Exception as exc:  # noqa: BLE001
        checks["cache"] = f"error: {exc}"

    checks["celery_broker"] = _check_celery_broker()

    critical = {k: v for k, v in checks.items() if k != "celery_broker" or v != "skipped"}
    ok = all(v == "ok" or v == "skipped" for v in critical.values())
    payload: dict[str, Any] = {
        "status": "ok" if ok else "degraded",
        "checks": checks,
        "release": _release(),
    }
    return JsonResponse(payload, status=200 if ok else 503)


def metricsz(_request):
    """Lightweight operational metrics for launch monitoring (no Prometheus required)."""
    since = timezone.now() - timedelta(hours=24)
    events_24h = 0
    revenue_cents_24h = 0
    open_actions = 0
    try:
        from apps.analytics.models import AnalyticsEvent

        events_24h = AnalyticsEvent.objects.filter(created_at__gte=since).count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("metricsz analytics skipped: %s", exc)
    try:
        from apps.monetization.models import RevenueEvent

        from django.db.models import Sum

        agg = RevenueEvent.objects.filter(created_at__gte=since).aggregate(
            total=Sum("amount_cents")
        )
        revenue_cents_24h = int(agg.get("total") or 0)
    except Exception as exc:  # noqa: BLE001
        logger.debug("metricsz revenue skipped: %s", exc)
    try:
        from apps.growth_agent.models import GrowthAction

        open_actions = GrowthAction.objects.filter(
            status=GrowthAction.Status.PROPOSED
        ).count()
    except Exception as exc:  # noqa: BLE001
        logger.debug("metricsz growth actions skipped: %s", exc)

    return JsonResponse(
        {
            "status": "ok",
            "release": _release(),
            "window_hours": 24,
            "analytics_events": events_24h,
            "revenue_cents": revenue_cents_24h,
            "growth_actions_proposed": open_actions,
        }
    )
