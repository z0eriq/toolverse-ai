from __future__ import annotations

from django.db import models

from apps.common.models import TimeStampedModel


class Category(TimeStampedModel):
    slug = models.SlugField(unique=True, max_length=64)
    name = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "slug"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.slug


class Tool(TimeStampedModel):
    class Source(models.TextChoices):
        FILESYSTEM = "filesystem", "Filesystem"
        DYNAMIC = "dynamic", "Dynamic"

    tool_id = models.CharField(max_length=128, unique=True, db_index=True)
    slug = models.SlugField(max_length=128, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="tools")
    name = models.JSONField(default=dict)
    description = models.JSONField(default=dict)
    version = models.CharField(max_length=32, default="1.0.0")
    premium = models.BooleanField(default=False)
    adsense_slot = models.CharField(max_length=32, default="sidebar")
    seo_title = models.JSONField(default=dict)
    seo_description = models.JSONField(default=dict, blank=True)
    seo_keywords = models.JSONField(default=list)
    schema_type = models.CharField(max_length=64, default="WebApplication")
    capabilities = models.JSONField(default=list)
    icon = models.CharField(max_length=64, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveBigIntegerField(default=0)
    search_document = models.TextField(blank=True, default="")
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.FILESYSTEM,
        db_index=True,
    )
    definition = models.OneToOneField(
        "tools_registry.DynamicToolDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_tool",
    )
    faq = models.JSONField(default=list, blank=True)
    howto_steps = models.JSONField(default=list, blank=True)
    related_slugs = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["order", "slug"]
        unique_together = (("category", "slug"),)
        indexes = [
            models.Index(fields=["category", "slug"]),
            models.Index(fields=["premium", "is_active"]),
            models.Index(fields=["source", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.tool_id

    def rebuild_search_document(self) -> None:
        parts: list[str] = [self.tool_id, self.slug]
        for mapping in (self.name, self.description, self.seo_title, self.seo_description):
            if isinstance(mapping, dict):
                parts.extend(str(v) for v in mapping.values())
        if isinstance(self.seo_keywords, list):
            parts.extend(str(k) for k in self.seo_keywords)
        self.search_document = " ".join(parts).lower()


from apps.tools_registry.dynamic_models import DynamicToolDefinition  # noqa: E402,F401
from apps.tools_registry.growth_models import ToolGrowthMeta  # noqa: E402,F401
