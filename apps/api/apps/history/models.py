from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class ToolHistory(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tool_history"
    )
    tool = models.ForeignKey(
        "tools_registry.Tool", on_delete=models.CASCADE, related_name="history_entries"
    )
    action = models.CharField(max_length=64, default="run")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.tool_id}:{self.action}"
