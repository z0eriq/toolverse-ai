from celery import shared_task

from apps.tools_registry.discovery import sync_tools_from_filesystem


@shared_task(name="apps.tools_registry.tasks.sync_tools_task")
def sync_tools_task() -> dict:
    return sync_tools_from_filesystem()
