from __future__ import annotations

import logging

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger("toolverse.content_factory")
User = get_user_model()


@shared_task(name="apps.content_factory.tasks.generate_content_task")
def generate_content_task(
    template_slug: str,
    variables: dict | None = None,
    content_id: int | None = None,
    user_id: int | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> dict:
    from apps.content_factory.services import generate_content

    user = None
    if user_id:
        user = User.objects.filter(pk=user_id).first()

    try:
        content = generate_content(
            template_slug,
            variables or {},
            user=user,
            content_id=content_id,
            provider=provider,
            model=model,
        )
        return {"content_id": content.pk, "slug": content.slug, "status": content.status}
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_content_task failed")
        return {"error": str(exc)[:2000], "content_id": content_id}


@shared_task(name="apps.content_factory.tasks.run_content_autopilot_task")
def run_content_autopilot_task(keyword_id: int, run_id: int | None = None) -> dict:
    from apps.content_factory.autopilot import run_content_autopilot

    try:
        run = run_content_autopilot(keyword_id, run_id=run_id)
        return {
            "run_id": run.pk,
            "status": run.status,
            "stage": run.stage,
            "content_item_id": run.content_item_id,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_content_autopilot_task failed")
        return {"error": str(exc)[:2000], "keyword_id": keyword_id, "run_id": run_id}
