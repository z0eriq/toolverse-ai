from __future__ import annotations

import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from apps.tool_factory.models import ToolFactoryJob

logger = logging.getLogger("toolverse.tool_factory")
User = get_user_model()


@shared_task(name="apps.tool_factory.tasks.build_tool_from_spec_task", bind=True)
def build_tool_from_spec_task(self, spec_id: int, user_id: int | None = None) -> dict:
    from apps.tool_factory.services import build_tool_from_spec

    user = None
    if user_id:
        user = User.objects.filter(pk=user_id).first()

    try:
        result = build_tool_from_spec(spec_id, user=user)
        job_id = result.get("job_id")
        if job_id:
            ToolFactoryJob.objects.filter(pk=job_id).update(celery_task_id=self.request.id or "")
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("build_tool_from_spec_task failed")
        return {"error": str(exc)[:2000], "spec_id": spec_id}
