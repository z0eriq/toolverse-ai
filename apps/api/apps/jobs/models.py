from django.conf import settings
from django.db import models
import uuid

from apps.common.models import TimeStampedModel


class AsyncJob(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="async_jobs",
    )
    tool_id = models.CharField(max_length=128, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    input_payload = models.JSONField(default=dict)
    output_payload = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    celery_task_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["tool_id", "status"]),
        ]
