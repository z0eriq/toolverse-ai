from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class WorkflowTemplate(TimeStampedModel):
    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    steps = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=64, blank=True, default="general", db_index=True)
    is_public = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.slug


class Workflow(TimeStampedModel):
    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        UNLISTED = "unlisted", "Unlisted"
        PUBLIC = "public", "Public"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workflows",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=160)
    steps = models.JSONField(default=list, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        db_index=True,
    )
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = (("owner", "slug"),)
        indexes = [
            models.Index(fields=["visibility", "-updated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.owner_id}:{self.slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:150] or "workflow"
        super().save(*args, **kwargs)


class WorkflowRun(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_runs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    input = models.JSONField(default=dict, blank=True)
    output = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True, default="")
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workflow", "-created_at"])]

    def __str__(self) -> str:
        return f"run:{self.workflow_id}:{self.status}"


class WorkflowUsageDaily(models.Model):
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="usage_daily",
    )
    date = models.DateField(db_index=True)
    runs = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = (("workflow", "date"),)

    def __str__(self) -> str:
        return f"{self.workflow_id}:{self.date}:{self.runs}"
