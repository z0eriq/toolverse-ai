from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class KeywordOpportunity(TimeStampedModel):
    keyword = models.CharField(max_length=512, db_index=True)
    locale = models.CharField(max_length=10, default="en", db_index=True)
    search_volume = models.PositiveIntegerField(default=0)
    difficulty = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    ranking_position = models.FloatField(null=True, blank=True)
    ctr = models.FloatField(default=0.0)
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    suggested_tool_slug = models.SlugField(max_length=128, blank=True, default="")
    priority_score = models.FloatField(default=0.0, db_index=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-priority_score", "-impressions"]
        unique_together = (("keyword", "locale"),)
        verbose_name = "Keyword opportunity"
        verbose_name_plural = "Keyword opportunities"
        indexes = [
            models.Index(fields=["-priority_score"]),
            models.Index(fields=["locale", "-search_volume"]),
        ]

    def __str__(self) -> str:
        return f"{self.keyword} ({self.locale})"
