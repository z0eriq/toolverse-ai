from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class GSCProperty(TimeStampedModel):
    site_url = models.URLField(max_length=512, unique=True)
    credentials_ref = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Env key or file path reference for service-account credentials",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "GSC property"
        verbose_name_plural = "GSC properties"
        ordering = ["site_url"]

    def __str__(self) -> str:
        return self.site_url


class GSCMetricSnapshot(models.Model):
    property = models.ForeignKey(
        GSCProperty,
        on_delete=models.CASCADE,
        related_name="snapshots",
        null=True,
        blank=True,
    )
    date = models.DateField(db_index=True)
    page = models.CharField(max_length=1024, blank=True, default="", db_index=True)
    query = models.CharField(max_length=512, blank=True, default="", db_index=True)
    country = models.CharField(max_length=8, blank=True, default="")
    device = models.CharField(max_length=32, blank=True, default="")
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    ctr = models.FloatField(default=0.0)
    position = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-clicks"]
        indexes = [
            models.Index(fields=["date", "page"]),
            models.Index(fields=["date", "query"]),
        ]

    def __str__(self) -> str:
        return f"{self.date}:{self.query or self.page}"


class IndexedUrl(TimeStampedModel):
    """SEO indexing status tracked from GSC page metrics and manual review."""

    class Status(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        SUBMITTED = "submitted", "Submitted"
        CRAWLED = "crawled", "Crawled"
        INDEXED = "indexed", "Indexed"
        ERROR = "error", "Error"

    url_path = models.CharField(max_length=1024, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
    )
    last_crawled_at = models.DateTimeField(null=True, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    position = models.FloatField(null=True, blank=True)
    ranking_delta = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-impressions", "url_path"]
        indexes = [
            models.Index(fields=["status", "-impressions"]),
            models.Index(fields=["-clicks"]),
        ]

    def __str__(self) -> str:
        return f"{self.url_path}:{self.status}"
