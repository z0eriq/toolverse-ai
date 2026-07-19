from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class CompetitorDomain(TimeStampedModel):
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["domain"]

    def __str__(self) -> str:
        return self.domain


class CompetitorKeyword(TimeStampedModel):
    competitor = models.ForeignKey(
        CompetitorDomain,
        on_delete=models.CASCADE,
        related_name="keywords",
    )
    keyword = models.CharField(max_length=255, db_index=True)
    position = models.FloatField(default=0.0)
    search_volume = models.PositiveIntegerField(default=0)
    our_has_coverage = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-search_volume", "keyword"]
        unique_together = (("competitor", "keyword"),)

    def __str__(self) -> str:
        return f"{self.competitor_id}:{self.keyword}"


class CompetitorOpportunity(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        QUEUED = "queued", "Queued"
        DONE = "done", "Done"
        DISMISSED = "dismissed", "Dismissed"

    competitor = models.ForeignKey(
        CompetitorDomain,
        on_delete=models.CASCADE,
        related_name="opportunities",
    )
    keyword = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True, default="")
    gap_score = models.FloatField(default=0.0, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-gap_score", "-created_at"]
        unique_together = (("competitor", "keyword"),)
        indexes = [models.Index(fields=["status", "-gap_score"])]

    def __str__(self) -> str:
        return self.title
