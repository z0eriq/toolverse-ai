from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class ToolSpec(TimeStampedModel):
    class Recipe(models.TextChoices):
        GENERIC = "generic", "Generic"
        PDF = "pdf", "PDF"
        IMAGE = "image", "Image"
        AI = "ai", "AI"
        DEVELOPER = "developer", "Developer"
        CALCULATOR = "calculator", "Calculator"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATING = "generating", "Generating"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        PUBLISHED = "published", "Published"

    slug = models.SlugField(max_length=128, unique=True)
    category_slug = models.SlugField(max_length=64, default="ai")
    name = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    ui_schema = models.JSONField(default=dict, blank=True)
    pipeline = models.JSONField(default=list, blank=True)
    seo = models.JSONField(default=dict, blank=True)
    faq = models.JSONField(default=list, blank=True)
    howto = models.JSONField(default=list, blank=True)
    capabilities = models.JSONField(default=list, blank=True)
    recipe = models.CharField(
        max_length=32,
        choices=Recipe.choices,
        default=Recipe.GENERIC,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    error = models.TextField(blank=True, default="")
    is_viral = models.BooleanField(default=False)
    share_text = models.JSONField(default=dict, blank=True)
    export_filesystem = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tool_specs",
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.slug


class ToolFactoryJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    spec = models.ForeignKey(
        ToolSpec,
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    log = models.JSONField(default=list, blank=True)
    artifacts = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"job:{self.spec_id}:{self.status}"
