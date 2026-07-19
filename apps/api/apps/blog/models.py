from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class BlogTag(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class BlogPost(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts",
    )
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")
    published_at = models.DateTimeField(null=True, blank=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240]
        super().save(*args, **kwargs)
