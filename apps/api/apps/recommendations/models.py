from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class ToolAffinity(TimeStampedModel):
    """Pairwise affinity score between two tools (undirected; tool_a_id < tool_b_id)."""

    tool_a = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="affinities_as_a",
    )
    tool_b = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="affinities_as_b",
    )
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = (("tool_a", "tool_b"),)
        ordering = ["-score"]
        indexes = [
            models.Index(fields=["tool_a", "-score"]),
            models.Index(fields=["tool_b", "-score"]),
        ]
        verbose_name_plural = "tool affinities"

    def __str__(self) -> str:
        return f"{self.tool_a_id}<->{self.tool_b_id}:{self.score:.3f}"


class ToolRelationship(TimeStampedModel):
    """Directed relationship score used to enrich related-tool recommendations."""

    source_tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="relationships_out",
    )
    target_tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="relationships_in",
    )
    relationship_score = models.FloatField(default=0.0)
    reason = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = (("source_tool", "target_tool"),)
        ordering = ["-relationship_score"]
        indexes = [
            models.Index(fields=["source_tool", "-relationship_score"]),
        ]

    def __str__(self) -> str:
        return f"{self.source_tool_id}->{self.target_tool_id}:{self.relationship_score:.3f}"
