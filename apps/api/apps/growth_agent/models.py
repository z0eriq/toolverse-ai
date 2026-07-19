from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class GrowthInsight(TimeStampedModel):
    class Category(models.TextChoices):
        TRAFFIC = "traffic", "Traffic"
        SEO = "seo", "SEO"
        TOOLS = "tools", "Tools"
        REVENUE = "revenue", "Revenue"
        CONTENT = "content", "Content"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DISMISSED = "dismissed", "Dismissed"

    category = models.CharField(max_length=32, choices=Category.choices, db_index=True)
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True, default="")
    priority = models.IntegerField(default=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    meta = models.JSONField(default=dict, blank=True)
    source_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-priority"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.category}:{self.title}"


class GrowthAgentRun(TimeStampedModel):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        db_index=True,
    )
    summary = models.TextField(blank=True, default="")
    insights_created = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True, default="")
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"run:{self.pk}:{self.status}"


class GrowthTask(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DONE = "done", "Done"
        DISMISSED = "dismissed", "Dismissed"

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=32, db_index=True, blank=True, default="")
    priority = models.IntegerField(default=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    insight = models.ForeignKey(
        GrowthInsight,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-priority"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return self.title


class GrowthAction(TimeStampedModel):
    class ActionType(models.TextChoices):
        CREATE_SEO_TASK = "create_seo_task", "Create SEO task"
        QUEUE_TOOL_SPEC = "queue_tool_spec", "Queue tool spec"
        START_AUTOPILOT = "start_autopilot", "Start autopilot"
        CREATE_CONTENT_DRAFT = "create_content_draft", "Create content draft"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        APPROVED = "approved", "Approved"
        EXECUTED = "executed", "Executed"
        REJECTED = "rejected", "Rejected"
        FAILED = "failed", "Failed"

    task = models.ForeignKey(
        GrowthTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions",
    )
    action_type = models.CharField(
        max_length=32,
        choices=ActionType.choices,
        db_index=True,
    )
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED,
        db_index=True,
    )
    result_ref = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "action_type"]),
            models.Index(fields=["action_type", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action_type}:{self.status}:{self.pk}"
