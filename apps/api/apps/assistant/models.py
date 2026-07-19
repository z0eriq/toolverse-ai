from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class AssistantSession(TimeStampedModel):
    """Optional chat session for multi-turn assistant conversations."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assistant_sessions",
    )
    session_key = models.CharField(max_length=64, blank=True, default="", db_index=True)
    messages = models.JSONField(default=list, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"session:{self.pk}"
