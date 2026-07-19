from __future__ import annotations

import logging
import os
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.launch_readiness.models import ReadinessCheck

logger = logging.getLogger("toolverse.launch_readiness")


def _upsert(
    *,
    key: str,
    category: str,
    status: str,
    detail: str,
) -> ReadinessCheck:
    obj, _ = ReadinessCheck.objects.update_or_create(
        key=key,
        defaults={
            "category": category,
            "status": status,
            "detail": detail[:2000],
            "checked_at": timezone.now(),
        },
    )
    return obj


def run_readiness_checks() -> list[ReadinessCheck]:
    """Probe launch readiness dimensions and persist ReadinessCheck rows."""
    results: list[ReadinessCheck] = []

    # Infra / env
    required = ("SECRET_KEY", "ALLOWED_HOSTS", "REDIS_URL", "CELERY_BROKER_URL")
    missing = [k for k in required if not (os.getenv(k) or getattr(settings, k, None))]
    secret = (os.getenv("SECRET_KEY") or getattr(settings, "SECRET_KEY", "") or "").strip()
    if missing:
        results.append(
            _upsert(
                key="env-required",
                category=ReadinessCheck.Category.INFRA,
                status=ReadinessCheck.Status.FAIL,
                detail=f"Missing: {', '.join(missing)}",
            )
        )
    elif secret in {
        "insecure-dev-key-change-me",
        "change-me",
        "insecure-dev-key",
    }:
        results.append(
            _upsert(
                key="env-required",
                category=ReadinessCheck.Category.INFRA,
                status=ReadinessCheck.Status.WARN,
                detail="SECRET_KEY looks like a development placeholder",
            )
        )
    else:
        results.append(
            _upsert(
                key="env-required",
                category=ReadinessCheck.Category.INFRA,
                status=ReadinessCheck.Status.PASS,
                detail="Core env keys present",
            )
        )

    backup = getattr(settings, "BACKUP_ENABLED", False)
    results.append(
        _upsert(
            key="backups",
            category=ReadinessCheck.Category.INFRA,
            status=ReadinessCheck.Status.PASS if backup else ReadinessCheck.Status.WARN,
            detail="BACKUP_ENABLED is on" if backup else "BACKUP_ENABLED is false",
        )
    )

    beat = getattr(settings, "CELERY_BEAT_SCHEDULE", {}) or {}
    results.append(
        _upsert(
            key="celery-beat",
            category=ReadinessCheck.Category.INFRA,
            status=ReadinessCheck.Status.PASS if beat else ReadinessCheck.Status.WARN,
            detail=f"{len(beat)} beat entries configured",
        )
    )

    # Security / monitoring
    sentry = getattr(settings, "SENTRY_DSN", "") or os.getenv("SENTRY_DSN", "")
    results.append(
        _upsert(
            key="sentry",
            category=ReadinessCheck.Category.MONITORING,
            status=ReadinessCheck.Status.PASS if sentry else ReadinessCheck.Status.WARN,
            detail="Sentry DSN configured" if sentry else "SENTRY_DSN not set",
        )
    )

    debug = bool(getattr(settings, "DEBUG", True))
    results.append(
        _upsert(
            key="debug-off",
            category=ReadinessCheck.Category.SECURITY,
            status=ReadinessCheck.Status.WARN if debug else ReadinessCheck.Status.PASS,
            detail="DEBUG is True" if debug else "DEBUG is False",
        )
    )

    # SEO
    gsc = getattr(settings, "GSC_CREDENTIALS_JSON", "") or getattr(
        settings, "GSC_CREDENTIALS_FILE", ""
    )
    results.append(
        _upsert(
            key="gsc-credentials",
            category=ReadinessCheck.Category.SEO,
            status=ReadinessCheck.Status.PASS if gsc else ReadinessCheck.Status.WARN,
            detail="GSC credentials present" if gsc else "GSC credentials optional / missing",
        )
    )

    # Analytics
    try:
        from apps.analytics.models import AnalyticsEvent

        count = AnalyticsEvent.objects.count()
        results.append(
            _upsert(
                key="analytics-events",
                category=ReadinessCheck.Category.ANALYTICS,
                status=ReadinessCheck.Status.PASS if count else ReadinessCheck.Status.WARN,
                detail=f"{count} AnalyticsEvent rows",
            )
        )
    except Exception as exc:  # noqa: BLE001
        results.append(
            _upsert(
                key="analytics-events",
                category=ReadinessCheck.Category.ANALYTICS,
                status=ReadinessCheck.Status.UNKNOWN,
                detail=str(exc)[:500],
            )
        )

    # Payments / premium plan
    try:
        from apps.subscriptions.models import Plan

        premium = Plan.objects.filter(slug__in=("premium", "pro"), is_active=True).exists()
        results.append(
            _upsert(
                key="premium-plan",
                category=ReadinessCheck.Category.PAYMENTS,
                status=ReadinessCheck.Status.PASS if premium else ReadinessCheck.Status.WARN,
                detail="Premium/Pro plan exists" if premium else "No premium/pro plan",
            )
        )
    except Exception as exc:  # noqa: BLE001
        results.append(
            _upsert(
                key="premium-plan",
                category=ReadinessCheck.Category.PAYMENTS,
                status=ReadinessCheck.Status.UNKNOWN,
                detail=str(exc)[:500],
            )
        )

    # Email
    email_backend = getattr(settings, "EMAIL_BACKEND", "") or ""
    console = "console" in email_backend.lower()
    results.append(
        _upsert(
            key="email-backend",
            category=ReadinessCheck.Category.EMAIL,
            status=ReadinessCheck.Status.WARN if console or not email_backend else ReadinessCheck.Status.PASS,
            detail=email_backend or "EMAIL_BACKEND unset (Django default)",
        )
    )

    logger.info("run_readiness_checks count=%s", len(results))
    return results


def readiness_payload() -> list[dict[str, Any]]:
    checks = list(ReadinessCheck.objects.all().order_by("category", "key"))
    if not checks:
        checks = run_readiness_checks()
    return [
        {
            "id": c.id,
            "key": c.key,
            "category": c.category,
            "status": c.status,
            "detail": c.detail,
            "checked_at": c.checked_at.isoformat() if c.checked_at else None,
        }
        for c in checks
    ]
