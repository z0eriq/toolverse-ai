from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Experiment(TimeStampedModel):
    key = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    variants = models.JSONField(
        default=list,
        help_text='List of {"key": "control", "weight": 50} objects',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key


class ExperimentAssignment(TimeStampedModel):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    subject_key = models.CharField(max_length=128, db_index=True)
    variant = models.CharField(max_length=64)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="experiment_assignments",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = (("experiment", "subject_key"),)
        indexes = [
            models.Index(fields=["experiment", "variant"]),
        ]

    def __str__(self) -> str:
        return f"{self.experiment_id}:{self.subject_key}:{self.variant}"


class ExperimentEvent(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="events",
    )
    assignment = models.ForeignKey(
        ExperimentAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    subject_key = models.CharField(max_length=128, db_index=True)
    variant = models.CharField(max_length=64, blank=True, default="")
    event_name = models.CharField(max_length=128, db_index=True)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["experiment", "event_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.experiment_id}:{self.event_name}"
