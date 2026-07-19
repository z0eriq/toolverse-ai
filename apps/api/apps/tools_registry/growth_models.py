from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class ToolGrowthMeta(TimeStampedModel):
    """Viral sharing and growth metadata for a Tool."""

    tool = models.OneToOneField(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="growth_meta",
    )
    is_viral = models.BooleanField(default=False, db_index=True)
    share_text = models.JSONField(default=dict, blank=True)
    og_template = models.CharField(max_length=64, blank=True, default="")
    share_platforms = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Tool growth meta"
        verbose_name_plural = "Tool growth meta"

    def __str__(self) -> str:
        return f"growth:{self.tool_id}"
