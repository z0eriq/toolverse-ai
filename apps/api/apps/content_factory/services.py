from __future__ import annotations

import logging
from string import Template
from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.ai_providers.base import AIProviderError
from apps.ai_providers.router import get_ai_router
from apps.content_factory.models import (
    ContentGenerationLog,
    ContentItem,
    ContentVersion,
    PromptTemplate,
)

logger = logging.getLogger("toolverse.content_factory")


def _render_template(template_text: str, variables: dict[str, Any]) -> str:
    safe = {k: str(v) for k, v in (variables or {}).items()}
    try:
        return Template(template_text).safe_substitute(safe)
    except Exception:  # noqa: BLE001
        return template_text


def _next_revision(content: ContentItem) -> int:
    last = content.versions.order_by("-revision").values_list("revision", flat=True).first()
    return int(last or 0) + 1


def _snapshot_meta(content: ContentItem) -> dict[str, Any]:
    return {
        "title": content.title,
        "meta_title": content.meta_title,
        "meta_description": content.meta_description,
        "status": content.status,
        "locale": content.locale,
        "target_path": content.target_path,
        "content_type": content.content_type,
    }


@transaction.atomic
def generate_content(
    template_slug: str,
    variables: dict[str, Any] | None = None,
    user=None,
    *,
    content_id: int | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> ContentItem:
    """
    Render a PromptTemplate, call the AI router, and persist ContentItem + version + log.
    """
    template = PromptTemplate.objects.get(slug=template_slug)
    variables = variables or {}
    prompt = _render_template(template.template_text, variables)

    log = ContentGenerationLog.objects.create(
        content_id=content_id,
        prompt=prompt[:8000],
        status=ContentGenerationLog.Status.QUEUED,
    )

    try:
        result = get_ai_router().complete(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a professional content writer for ToolVerse AI, "
                        "an online tools platform. Write clear, SEO-friendly content."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            provider=provider,
            model=model,
            temperature=0.4,
            max_tokens=2048,
            user=user,
            tool_id="content_factory",
        )
    except AIProviderError as exc:
        log.status = ContentGenerationLog.Status.ERROR
        log.error = str(exc)[:2000]
        log.save(update_fields=["status", "error"])
        raise

    body = (result.content or "").strip()
    title = str(variables.get("title") or variables.get("name") or template.name)[:255]
    locale = str(variables.get("locale") or template.locale or "en")[:10]
    content_type = str(variables.get("content_type") or template.purpose)[:64]

    if content_id:
        content = ContentItem.objects.select_for_update().get(pk=content_id)
        content.body = body
        content.status = ContentItem.Status.AI_GENERATED
        if variables.get("title"):
            content.title = title
        if variables.get("meta_title"):
            content.meta_title = str(variables["meta_title"])[:255]
        if variables.get("meta_description"):
            content.meta_description = str(variables["meta_description"])
        content.save()
    else:
        base_slug = slugify(str(variables.get("slug") or title))[:200] or "content"
        slug = base_slug
        n = 1
        while ContentItem.objects.filter(slug=slug).exists():
            n += 1
            slug = f"{base_slug}-{n}"
        content = ContentItem.objects.create(
            title=title,
            slug=slug,
            body=body,
            content_type=content_type,
            status=ContentItem.Status.AI_GENERATED,
            locale=locale,
            tool_id=variables.get("tool_id") or None,
            target_path=str(variables.get("target_path") or "")[:512],
            meta_title=str(variables.get("meta_title") or title)[:255],
            meta_description=str(variables.get("meta_description") or "")[:2000],
            created_by=user if getattr(user, "is_authenticated", False) else None,
        )

    ContentVersion.objects.create(
        content=content,
        revision=_next_revision(content),
        body=body,
        meta_snapshot=_snapshot_meta(content),
        created_by=user if getattr(user, "is_authenticated", False) else None,
    )

    log.content = content
    log.provider = result.provider
    log.model = result.model
    log.response_excerpt = body[:2000]
    log.tokens_in = result.tokens_in
    log.tokens_out = result.tokens_out
    log.status = ContentGenerationLog.Status.SUCCESS
    log.error = ""
    log.save()

    return content


def queue_regenerate(content_id: int, template_slug: str | None = None) -> str:
    """Enqueue Celery regeneration for an existing ContentItem. Returns task id."""
    from apps.content_factory.tasks import generate_content_task

    content = ContentItem.objects.get(pk=content_id)
    slug = template_slug or content.content_type
    async_result = generate_content_task.delay(
        template_slug=slug,
        variables={
            "title": content.title,
            "slug": content.slug,
            "locale": content.locale,
            "content_type": content.content_type,
            "target_path": content.target_path,
            "meta_title": content.meta_title,
            "meta_description": content.meta_description,
            "tool_id": content.tool_id,
        },
        content_id=content_id,
        user_id=content.created_by_id,
    )
    ContentGenerationLog.objects.create(
        content=content,
        prompt=f"queued regenerate via {slug}",
        status=ContentGenerationLog.Status.QUEUED,
    )
    return str(async_result.id)


def publish_content(content: ContentItem) -> ContentItem:
    content.status = ContentItem.Status.PUBLISHED
    content.published_at = timezone.now()
    content.save(update_fields=["status", "published_at", "updated_at"])
    ContentVersion.objects.create(
        content=content,
        revision=_next_revision(content),
        body=content.body,
        meta_snapshot=_snapshot_meta(content),
        created_by=content.created_by,
    )
    return content
