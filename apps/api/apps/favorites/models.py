from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Favorite(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    tool = models.ForeignKey("tools_registry.Tool", on_delete=models.CASCADE, related_name="favorited_by")

    class Meta:
        unique_together = (("user", "tool"),)
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.tool_id}"
