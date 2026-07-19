from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class PromptTemplate(TimeStampedModel):
    class Purpose(models.TextChoices):
        TOOL_DESCRIPTION = "tool_description", "Tool description"
        SEO_TITLE = "seo_title", "SEO title"
        META = "meta", "Meta description"
        FAQ = "faq", "FAQ"
        BLOG = "blog", "Blog"
        TUTORIAL = "tutorial", "Tutorial"
        COMPARISON = "comparison", "Comparison"
        LANDING = "landing", "Landing"

    slug = models.SlugField(unique=True, max_length=128)
    name = models.CharField(max_length=255)
    template_text = models.TextField()
    purpose = models.CharField(max_length=32, choices=Purpose.choices, db_index=True)
    locale = models.CharField(max_length=10, default="en", db_index=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.slug


class ContentItem(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        AI_GENERATED = "ai_generated", "AI generated"
        HUMAN_REVIEW = "human_review", "Human review"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    body = models.TextField(blank=True, default="")
    content_type = models.CharField(max_length=64, default="blog", db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    locale = models.CharField(max_length=10, default="en", db_index=True)
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_items",
    )
    target_path = models.CharField(max_length=512, blank=True, default="")
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_items",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "locale"]),
            models.Index(fields=["content_type", "status"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240] or "content"
        super().save(*args, **kwargs)


class ContentVersion(models.Model):
    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    revision = models.PositiveIntegerField()
    body = models.TextField(blank=True, default="")
    meta_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_versions",
    )

    class Meta:
        ordering = ["-revision"]
        unique_together = (("content", "revision"),)

    def __str__(self) -> str:
        return f"{self.content_id}#{self.revision}"


class ContentGenerationLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        QUEUED = "queued", "Queued"

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_logs",
    )
    provider = models.CharField(max_length=64, blank=True, default="")
    model = models.CharField(max_length=128, blank=True, default="")
    prompt = models.TextField(blank=True, default="")
    response_excerpt = models.TextField(blank=True, default="")
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.status}:{self.pk}"


class AutopilotRun(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        HUMAN_REVIEW = "human_review", "Human review"
        PUBLISHED = "published", "Published"
        FAILED = "failed", "Failed"

    keyword = models.ForeignKey(
        "keywords.KeywordOpportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autopilot_runs",
    )
    stage = models.CharField(max_length=64, blank=True, default="pending", db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autopilot_runs",
    )
    quality_score = models.FloatField(default=0.0)
    is_duplicate = models.BooleanField(default=False)
    error = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"autopilot:{self.pk}:{self.status}:{self.stage}"
