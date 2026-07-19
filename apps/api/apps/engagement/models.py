from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class SavedOutput(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_outputs",
    )
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="saved_outputs",
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.title}"


class Collection(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collections",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    description = models.TextField(blank=True, default="")
    is_public = models.BooleanField(default=False, db_index=True)
    public_slug = models.SlugField(max_length=160, blank=True, null=True, unique=True)

    class Meta:
        ordering = ["name"]
        unique_together = (("user", "slug"),)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:130] or "collection"
        if self.is_public and not self.public_slug:
            base = slugify(self.name)[:140] or "collection"
            candidate = base
            n = 1
            while (
                Collection.objects.filter(public_slug=candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                n += 1
                candidate = f"{base}-{n}"
            self.public_slug = candidate
        super().save(*args, **kwargs)


class CollectionItem(TimeStampedModel):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="collection_items",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = (("collection", "tool"),)

    def __str__(self) -> str:
        return f"{self.collection_id}:{self.tool_id}"


class ToolReview(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tool_reviews",
    )
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True, default="")
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = (("user", "tool"),)
        indexes = [models.Index(fields=["tool", "status"])]

    def __str__(self) -> str:
        return f"{self.tool_id}:{self.rating}"


class ToolComment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tool_comments",
    )
    tool = models.ForeignKey(
        "tools_registry.Tool",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["tool", "status"])]

    def __str__(self) -> str:
        return f"comment:{self.pk}"
