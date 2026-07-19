from __future__ import annotations

from celery import shared_task


@shared_task(name="apps.launch_readiness.tasks.run_readiness_checks_daily")
def run_readiness_checks_daily() -> dict:
    from apps.launch_readiness.services import run_readiness_checks

    try:
        checks = run_readiness_checks()
        return {"count": len(checks)}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:2000]}
