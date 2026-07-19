from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class SeoRecommendation(TimeStampedModel):
    class Type(models.TextChoices):
        TITLE = "title", "Title"
        META = "meta", "Meta"
        FAQ = "faq", "FAQ"
        INTERNAL_LINK = "internal_link", "Internal link"
        CONTENT = "content", "Content"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DISMISSED = "dismissed", "Dismissed"

    path = models.CharField(max_length=512, db_index=True)
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_recommendations",
    )
    type = models.CharField(max_length=32, choices=Type.choices, db_index=True)
    severity = models.CharField(
        max_length=16,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    suggestion = models.TextField()
    rationale = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["path", "status"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.type}:{self.path}:{self.status}"


class SeoHealthScore(TimeStampedModel):
    path = models.CharField(max_length=512, unique=True, db_index=True)
    metadata = models.FloatField(default=0.0)
    schema = models.FloatField(default=0.0)
    internal_links = models.FloatField(default=0.0)
    content_quality = models.FloatField(default=0.0)
    keyword_coverage = models.FloatField(default=0.0)
    performance = models.FloatField(default=70.0)
    overall = models.FloatField(default=0.0, db_index=True)
    recommendations = models.JSONField(default=list, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-overall", "path"]
        indexes = [
            models.Index(fields=["-overall"]),
            models.Index(fields=["-analyzed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.path}:{self.overall:.1f}"


class SeoOpportunityTask(TimeStampedModel):
    class Source(models.TextChoices):
        KEYWORD = "keyword", "Keyword"
        GSC = "gsc", "GSC"
        HEALTH = "health", "Health"
        OPPORTUNITY = "opportunity", "Opportunity"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"
        DISMISSED = "dismissed", "Dismissed"

    class SuggestedAction(models.TextChoices):
        CREATE_TOOL = "create_tool", "Create tool"
        WRITE_CONTENT = "write_content", "Write content"
        FIX_SEO = "fix_seo", "Fix SEO"
        INTERNAL_LINKS = "internal_links", "Internal links"

    source = models.CharField(max_length=32, choices=Source.choices, db_index=True)
    title = models.CharField(max_length=255)
    rationale = models.TextField(blank=True, default="")
    priority = models.IntegerField(default=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    suggested_action = models.CharField(
        max_length=32,
        choices=SuggestedAction.choices,
        default=SuggestedAction.WRITE_CONTENT,
    )
    path = models.CharField(max_length=512, blank=True, default="")
    keyword = models.ForeignKey(
        "keywords.KeywordOpportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_opportunity_tasks",
    )
    tool_opportunity = models.ForeignKey(
        "tool_intelligence.ToolOpportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_opportunity_tasks",
    )

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-priority"]),
            models.Index(fields=["source", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.source}:{self.title}"


class SeoAutopilotRun(TimeStampedModel):
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
    issues_created = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True, default="")
    error = models.TextField(blank=True, default="")
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"seo-autopilot:{self.pk}:{self.status}"


class SeoPageIssue(TimeStampedModel):
    class IssueType(models.TextChoices):
        META = "meta", "Meta"
        FAQ = "faq", "FAQ"
        INTERNAL_LINK = "internal_link", "Internal link"
        FRESHNESS = "freshness", "Freshness"
        BROKEN_LINK = "broken_link", "Broken link"
        CTR = "ctr", "CTR"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        APPLIED = "applied", "Applied"
        DISMISSED = "dismissed", "Dismissed"

    run = models.ForeignKey(
        SeoAutopilotRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
    )
    path = models.CharField(max_length=512, db_index=True)
    issue_type = models.CharField(max_length=32, choices=IssueType.choices, db_index=True)
    severity = models.CharField(
        max_length=16,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    suggestion = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    evidence = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["path", "status"]),
            models.Index(fields=["issue_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.issue_type}:{self.path}:{self.status}"


class SeoApplyLog(TimeStampedModel):
    issue = models.ForeignKey(
        SeoPageIssue,
        on_delete=models.CASCADE,
        related_name="apply_logs",
    )
    applied_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_apply_logs",
    )
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    note = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"apply:{self.issue_id}:{self.pk}"
