from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.jobs.models import AsyncJob

logger = logging.getLogger("toolverse.jobs")


@shared_task(bind=True, name="apps.jobs.tasks.execute_tool_job")
def execute_tool_job(self, job_id: str) -> dict:
    try:
        job = AsyncJob.objects.get(pk=job_id)
    except AsyncJob.DoesNotExist:
        return {"error": "not_found"}

    job.status = AsyncJob.Status.RUNNING
    job.progress = 10
    job.celery_task_id = self.request.id or ""
    job.save(update_fields=["status", "progress", "celery_task_id", "updated_at"])

    try:
        result = _dispatch(job)
        job.output_payload = result
        job.status = AsyncJob.Status.SUCCEEDED
        job.progress = 100
        job.error = ""
        job.save(update_fields=["output_payload", "status", "progress", "error", "updated_at"])
        return {"job_id": str(job.id), "status": job.status}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Job %s failed", job_id)
        job.status = AsyncJob.Status.FAILED
        job.error = str(exc)[:2000]
        job.progress = 100
        job.save(update_fields=["status", "error", "progress", "updated_at"])
        return {"job_id": str(job.id), "status": job.status, "error": job.error}


def _dispatch(job: AsyncJob) -> dict:
    tool_id = job.tool_id
    payload = job.input_payload or {}

    # Dynamic tool pipeline
    if tool_id.startswith("dynamic:") or payload.get("source") == "dynamic":
        from apps.tools_registry.dynamic_runtime import execute_dynamic_pipeline

        slug = payload.get("slug") or tool_id.replace("dynamic:", "")
        return execute_dynamic_pipeline(slug, payload, user=job.user)

    # Filesystem plugin async hook
    from apps.tools_registry.discovery import load_tool_plugins

    plugins = load_tool_plugins()
    plugin = plugins.get(tool_id)
    if plugin is not None and hasattr(plugin, "run_async"):
        return plugin.run_async(payload)  # type: ignore[no-any-return]

    # Fallback: AI complete if requested
    if payload.get("ai"):
        from apps.ai_providers.router import get_ai_router

        messages = payload.get("messages") or [
            {"role": "user", "content": str(payload.get("prompt") or "")}
        ]
        result = get_ai_router().complete(
            messages,
            provider=payload.get("provider"),
            model=payload.get("model"),
            user=job.user,
            tool_id=tool_id,
        )
        return {
            "content": result.content,
            "provider": result.provider,
            "model": result.model,
        }

    raise ValueError(f"No async handler for tool '{tool_id}'")


@shared_task(name="apps.jobs.tasks.cleanup_old_jobs")
def cleanup_old_jobs(days: int = 7) -> dict:
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = AsyncJob.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted}
