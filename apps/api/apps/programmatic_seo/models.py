from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class ProgrammaticPage(TimeStampedModel):
    class PageType(models.TextChoices):
        BEST_OF = "best_of", "Best of"
        KEYWORD = "keyword", "Keyword"
        AUDIENCE = "audience", "Audience"
        CATEGORY_HUB = "category_hub", "Category hub"
        AUTHORITY = "authority", "Authority"
        USE_CASE = "use_case", "Use case"
        INDUSTRY = "industry", "Industry"
        COMPARISON = "comparison", "Comparison"
        TUTORIAL = "tutorial", "Tutorial"
        TOOL = "tool", "Tool"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Unique path key, e.g. best/pdf-tools or json/json-formatter-online",
    )
    path_pattern = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Pattern template, e.g. best/{topic}, tools/for-{audience}",
    )
    title = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    body = models.JSONField(default=dict, blank=True)
    page_type = models.CharField(
        max_length=32,
        choices=PageType.choices,
        default=PageType.KEYWORD,
        db_index=True,
    )
    topic = models.CharField(max_length=128, blank=True, default="")
    category_slug = models.CharField(max_length=64, blank=True, default="", db_index=True)
    audience = models.CharField(max_length=128, blank=True, default="")
    keyword = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    related_tool_ids = models.JSONField(default=list, blank=True)
    seo_title = models.JSONField(default=dict, blank=True)
    seo_description = models.JSONField(default=dict, blank=True)
    seo_keywords = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["slug"]
        indexes = [
            models.Index(fields=["status", "page_type"]),
            models.Index(fields=["category_slug", "status"]),
        ]

    def __str__(self) -> str:
        return self.slug

    @property
    def path(self) -> str:
        return self.slug.strip("/")
