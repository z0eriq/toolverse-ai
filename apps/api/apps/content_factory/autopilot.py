from __future__ import annotations

import logging
from difflib import SequenceMatcher
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify

from apps.content_factory.models import AutopilotRun, ContentItem
from apps.content_factory.services import publish_content
from apps.keywords.models import KeywordOpportunity

logger = logging.getLogger("toolverse.content_autopilot")


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _is_duplicate_title(title: str, *, exclude_id: int | None = None) -> bool:
    qs = ContentItem.objects.all()
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    for existing in qs.values_list("id", "title")[:500]:
        if _title_similarity(title, existing[1]) >= 0.85:
            return True
    return False


def _build_body(keyword: str, locale: str) -> str:
    return (
        f"# {keyword.title()}\n\n"
        f"This guide covers **{keyword}** for ToolVerse AI users "
        f"(locale: {locale}).\n\n"
        f"## Overview\n\n"
        f"Discover free online tools related to {keyword}. "
        f"Use our catalog to compare options, improve workflow, and ship faster.\n\n"
        f"## How to get started\n\n"
        f"1. Identify your goal around {keyword}.\n"
        f"2. Pick a matching ToolVerse tool.\n"
        f"3. Run it in the browser — no install required.\n"
    )


def _build_faq(keyword: str) -> list[dict[str, str]]:
    return [
        {
            "question": f"What is {keyword}?",
            "answer": f"{keyword.title()} refers to common search intent we cover with free online tools.",
        },
        {
            "question": f"Are tools for {keyword} free?",
            "answer": "Yes. Core ToolVerse tools are free to use in the browser.",
        },
        {
            "question": f"How do I choose the best tool for {keyword}?",
            "answer": "Compare features, privacy, and SEO relevance — then try the top matches.",
        },
    ]


def _link_suggestions(keyword: str) -> list[dict[str, str]]:
    slug = slugify(keyword)[:80] or "tools"
    return [
        {"title": f"Best tools for {keyword}", "path": f"/best/{slug}"},
        {"title": "All tools", "path": "/tools"},
        {"title": "Developers API", "path": "/developers"},
    ]


def _quality_score(body: str, faq: list, is_duplicate: bool) -> float:
    score = min(100.0, len(body) / 20.0 + len(faq) * 10.0)
    if is_duplicate:
        score *= 0.4
    return round(score, 2)


@transaction.atomic
def run_content_autopilot(keyword_id: int, *, run_id: int | None = None) -> AutopilotRun:
    """
    Stage pipeline: research → generate → faq → optimize → links →
    duplicate_check → human_review (or published if AUTOPILOT_AUTO_PUBLISH).
    """
    try:
        keyword = KeywordOpportunity.objects.get(pk=keyword_id)
    except KeywordOpportunity.DoesNotExist:
        if run_id:
            run = AutopilotRun.objects.get(pk=run_id)
            run.status = AutopilotRun.Status.FAILED
            run.error = f"KeywordOpportunity {keyword_id} not found"
            run.stage = "failed"
            run.save(update_fields=["status", "error", "stage", "updated_at"])
            return run
        raise

    if run_id:
        run = AutopilotRun.objects.select_for_update().get(pk=run_id)
    else:
        run = AutopilotRun.objects.create(
            keyword=keyword,
            status=AutopilotRun.Status.PENDING,
            stage="pending",
        )

    run.status = AutopilotRun.Status.RUNNING
    run.error = ""
    run.save(update_fields=["status", "error", "updated_at"])

    meta: dict[str, Any] = dict(run.meta or {})

    try:
        # research
        run.stage = "research"
        run.save(update_fields=["stage", "updated_at"])
        meta["research"] = {
            "keyword": keyword.keyword,
            "search_volume": keyword.search_volume,
            "difficulty": keyword.difficulty,
            "impressions": keyword.impressions,
        }

        # generate
        run.stage = "generate"
        run.save(update_fields=["stage", "updated_at"])
        title = f"{keyword.keyword.title()} — Free Online Tools Guide"
        body = _build_body(keyword.keyword, keyword.locale)
        base_slug = slugify(f"autopilot-{keyword.keyword}")[:200] or "autopilot-content"
        slug = base_slug
        n = 1
        while ContentItem.objects.filter(slug=slug).exists():
            n += 1
            slug = f"{base_slug}-{n}"

        content = ContentItem.objects.create(
            title=title[:255],
            slug=slug,
            body=body,
            content_type="blog",
            status=ContentItem.Status.AI_GENERATED,
            locale=keyword.locale or "en",
            target_path=f"/blog/{slug}",
            meta_title=title[:255],
            meta_description=f"Guide to {keyword.keyword} with free ToolVerse AI tools."[:2000],
        )
        run.content_item = content

        # faq
        run.stage = "faq"
        run.save(update_fields=["stage", "content_item", "updated_at"])
        faq = _build_faq(keyword.keyword)
        meta["faq"] = faq

        # optimize (seo_optimizer if available)
        run.stage = "optimize"
        run.save(update_fields=["stage", "updated_at"])
        seo_result: dict[str, Any] = {"skipped": True}
        try:
            from apps.seo_optimizer.services import analyze_page

            recs = analyze_page(content.target_path or f"/blog/{content.slug}")
            seo_result = {
                "skipped": False,
                "recommendations": [
                    {"type": r.type, "severity": r.severity, "suggestion": r.suggestion}
                    for r in recs
                ],
            }
            # Light meta polish from heuristics
            if content.meta_description and len(content.meta_description) < 70:
                content.meta_description = (
                    f"Learn about {keyword.keyword}: free tools, tips, and FAQs on ToolVerse AI."
                )[:2000]
                content.save(update_fields=["meta_description", "updated_at"])
        except Exception as exc:  # noqa: BLE001
            logger.info("Autopilot SEO optimize skipped: %s", exc)
            seo_result = {"skipped": True, "error": str(exc)[:500]}
        meta["seo"] = seo_result

        # links
        run.stage = "links"
        run.save(update_fields=["stage", "updated_at"])
        meta["link_suggestions"] = _link_suggestions(keyword.keyword)

        # duplicate check
        run.stage = "duplicate_check"
        run.save(update_fields=["stage", "updated_at"])
        is_dup = _is_duplicate_title(content.title, exclude_id=content.pk)
        run.is_duplicate = is_dup
        meta["duplicate_check"] = {"is_duplicate": is_dup}

        run.quality_score = _quality_score(content.body, faq, is_dup)
        run.meta = meta

        auto_publish = bool(getattr(settings, "AUTOPILOT_AUTO_PUBLISH", False))
        if auto_publish and not is_dup:
            run.stage = "published"
            run.status = AutopilotRun.Status.PUBLISHED
            publish_content(content)
        else:
            run.stage = "human_review"
            run.status = AutopilotRun.Status.HUMAN_REVIEW
            content.status = ContentItem.Status.HUMAN_REVIEW
            content.save(update_fields=["status", "updated_at"])

        run.save(
            update_fields=[
                "stage",
                "status",
                "is_duplicate",
                "quality_score",
                "meta",
                "content_item",
                "updated_at",
            ]
        )
        return run

    except Exception as exc:  # noqa: BLE001
        logger.exception("run_content_autopilot failed")
        run.status = AutopilotRun.Status.FAILED
        run.error = str(exc)[:2000]
        run.meta = meta
        run.save(update_fields=["status", "error", "meta", "updated_at"])
        return run


def approve_autopilot_run(run: AutopilotRun) -> AutopilotRun:
    if not run.content_item_id:
        raise ValueError("Autopilot run has no content item")
    publish_content(run.content_item)
    run.status = AutopilotRun.Status.PUBLISHED
    run.stage = "published"
    run.save(update_fields=["status", "stage", "updated_at"])
    return run
