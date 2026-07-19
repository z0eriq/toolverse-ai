from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class ToolTemplate(TimeStampedModel):
    slug = models.SlugField(max_length=128, unique=True)
    category_slug = models.SlugField(max_length=64, db_index=True)
    recipe = models.CharField(max_length=32, default="generic")
    ui_schema = models.JSONField(default=dict, blank=True)
    pipeline = models.JSONField(default=list, blank=True)
    priority_weight = models.FloatField(default=1.0)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.slug


class ToolOpportunity(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        QUEUED = "queued", "Queued"
        BUILT = "built", "Built"
        DISMISSED = "dismissed", "Dismissed"

    suggested_slug = models.SlugField(max_length=128, unique=True)
    category_slug = models.SlugField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True, default="")
    seo_score = models.FloatField(default=0.0)
    demand_score = models.FloatField(default=0.0)
    competition_score = models.FloatField(default=0.0)
    value_score = models.FloatField(default=0.0)
    priority_score = models.FloatField(default=0.0, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    keywords = models.ManyToManyField(
        "keywords.KeywordOpportunity",
        blank=True,
        related_name="tool_opportunities",
    )
    tool_spec = models.ForeignKey(
        "tool_factory.ToolSpec",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )

    class Meta:
        ordering = ["-priority_score"]
        verbose_name_plural = "Tool opportunities"

    def __str__(self) -> str:
        return self.suggested_slug


class ToolPerformanceScore(TimeStampedModel):
    """Live performance scores for published tools (0–100 scales)."""

    tool = models.OneToOneField(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="performance_score",
    )
    traffic_score = models.FloatField(default=0.0)
    usage_score = models.FloatField(default=0.0)
    revenue_score = models.FloatField(default=0.0)
    seo_score = models.FloatField(default=0.0)
    retention_score = models.FloatField(default=0.0)
    priority_score = models.FloatField(default=0.0, db_index=True)
    computed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-priority_score"]

    def __str__(self) -> str:
        return f"{self.tool_id}:{self.priority_score:.1f}"
