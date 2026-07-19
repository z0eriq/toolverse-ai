from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.history.models import ToolHistory


@shared_task(name="apps.history.tasks.cleanup_old_history")
def cleanup_old_history(days: int = 180) -> dict:
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = ToolHistory.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted}
