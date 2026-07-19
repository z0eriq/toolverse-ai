from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class DynamicToolDefinition(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(max_length=128, unique=True)
    category_slug = models.SlugField(max_length=64, default="ai")
    name = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    version = models.CharField(max_length=32, default="1.0.0")
    revision = models.PositiveIntegerField(default=1)
    premium = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    ui_schema = models.JSONField(default=dict, blank=True)
    pipeline = models.JSONField(default=list, blank=True)
    seo = models.JSONField(default=dict, blank=True)
    faq = models.JSONField(default=list, blank=True)
    howto_steps = models.JSONField(default=list, blank=True)
    capabilities = models.JSONField(default=list, blank=True)
    icon = models.CharField(max_length=64, blank=True)
    adsense_slot = models.CharField(max_length=32, default="sidebar")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dynamic_tools",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug and isinstance(self.name, dict):
            self.slug = slugify(self.name.get("en") or "tool")[:120]
        super().save(*args, **kwargs)

    def mark_published(self) -> None:
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.revision += 1
