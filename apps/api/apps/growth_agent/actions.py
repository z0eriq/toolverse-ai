"""Propose and execute GrowthAction artifacts — never auto-publish."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils.text import slugify

from apps.growth_agent.models import GrowthAction, GrowthAgentRun, GrowthTask

logger = logging.getLogger("toolverse.growth_agent")


def propose_growth_actions(run: GrowthAgentRun) -> list[GrowthAction]:
    """
    Create proposed GrowthAction rows from open ToolOpportunities,
    top keywords, and low SeoHealthScore paths.
    """
    created: list[GrowthAction] = []
    task_by_category = {
        t.category: t
        for t in GrowthTask.objects.filter(status=GrowthTask.Status.OPEN).order_by(
            "-priority"
        )[:50]
    }

    try:
        from apps.tool_intelligence.models import ToolOpportunity

        for opp in ToolOpportunity.objects.filter(
            status=ToolOpportunity.Status.OPEN
        ).order_by("-priority_score")[:10]:
            action = GrowthAction.objects.create(
                task=task_by_category.get("tools"),
                action_type=GrowthAction.ActionType.QUEUE_TOOL_SPEC,
                payload={
                    "opportunity_id": opp.pk,
                    "suggested_slug": opp.suggested_slug,
                    "title": opp.title,
                    "run_id": run.pk,
                },
                status=GrowthAction.Status.PROPOSED,
            )
            created.append(action)
    except Exception as exc:  # noqa: BLE001
        logger.debug("propose tool opportunities skipped: %s", exc)

    try:
        from apps.keywords.models import KeywordOpportunity

        for kw in KeywordOpportunity.objects.order_by("-priority_score")[:8]:
            action_type = (
                GrowthAction.ActionType.START_AUTOPILOT
                if float(kw.priority_score or 0) >= 70
                else GrowthAction.ActionType.CREATE_CONTENT_DRAFT
            )
            action = GrowthAction.objects.create(
                task=task_by_category.get("content") or task_by_category.get("seo"),
                action_type=action_type,
                payload={
                    "keyword_id": kw.pk,
                    "keyword": kw.keyword,
                    "locale": getattr(kw, "locale", "en") or "en",
                    "run_id": run.pk,
                },
                status=GrowthAction.Status.PROPOSED,
            )
            created.append(action)
            # Also propose an SEO task for high-impression keywords
            if int(getattr(kw, "impressions", 0) or 0) >= 100:
                seo_action = GrowthAction.objects.create(
                    task=task_by_category.get("seo"),
                    action_type=GrowthAction.ActionType.CREATE_SEO_TASK,
                    payload={
                        "keyword_id": kw.pk,
                        "keyword": kw.keyword,
                        "title": f"Optimize for “{kw.keyword}”",
                        "source": "keyword",
                        "run_id": run.pk,
                    },
                    status=GrowthAction.Status.PROPOSED,
                )
                created.append(seo_action)
    except Exception as exc:  # noqa: BLE001
        logger.debug("propose keywords skipped: %s", exc)

    try:
        from apps.seo_optimizer.models import SeoHealthScore

        for score in SeoHealthScore.objects.filter(overall__lt=70).order_by("overall")[
            :10
        ]:
            action = GrowthAction.objects.create(
                task=task_by_category.get("seo"),
                action_type=GrowthAction.ActionType.CREATE_SEO_TASK,
                payload={
                    "path": score.path,
                    "overall": score.overall,
                    "title": f"Fix SEO health on {score.path}",
                    "source": "health",
                    "suggested_action": "fix_seo",
                    "run_id": run.pk,
                },
                status=GrowthAction.Status.PROPOSED,
            )
            created.append(action)
    except Exception as exc:  # noqa: BLE001
        logger.debug("propose seo health skipped: %s", exc)

    return created


@transaction.atomic
def execute_growth_action(action: GrowthAction, *, user=None) -> GrowthAction:
    """
    Execute an approved GrowthAction.

    Creates draft / human_review artifacts only — NEVER published content.
    """
    if action.status in {
        GrowthAction.Status.EXECUTED,
        GrowthAction.Status.REJECTED,
    }:
        return action

    action.status = GrowthAction.Status.APPROVED
    action.error = ""
    action.save(update_fields=["status", "error", "updated_at"])

    try:
        result = _dispatch(action, user=user)
        action.result_ref = result
        action.status = GrowthAction.Status.EXECUTED
        action.save(update_fields=["result_ref", "status", "updated_at"])
    except Exception as exc:  # noqa: BLE001
        logger.exception("execute_growth_action failed action_id=%s", action.pk)
        action.status = GrowthAction.Status.FAILED
        action.error = str(exc)[:2000]
        action.save(update_fields=["status", "error", "updated_at"])
    return action


def _dispatch(action: GrowthAction, *, user=None) -> dict[str, Any]:
    payload = action.payload or {}
    if action.action_type == GrowthAction.ActionType.CREATE_SEO_TASK:
        return _create_seo_task(payload)
    if action.action_type == GrowthAction.ActionType.QUEUE_TOOL_SPEC:
        return _queue_tool_spec(payload, user=user)
    if action.action_type == GrowthAction.ActionType.START_AUTOPILOT:
        return _start_autopilot_draft(payload)
    if action.action_type == GrowthAction.ActionType.CREATE_CONTENT_DRAFT:
        return _create_content_draft(payload, user=user)
    raise ValueError(f"Unknown action_type: {action.action_type}")


def _create_seo_task(payload: dict[str, Any]) -> dict[str, Any]:
    from apps.seo_optimizer.models import SeoOpportunityTask

    source = payload.get("source") or SeoOpportunityTask.Source.OPPORTUNITY
    if source not in {c.value for c in SeoOpportunityTask.Source}:
        source = SeoOpportunityTask.Source.OPPORTUNITY
    suggested = payload.get("suggested_action") or SeoOpportunityTask.SuggestedAction.FIX_SEO
    if suggested not in {c.value for c in SeoOpportunityTask.SuggestedAction}:
        suggested = SeoOpportunityTask.SuggestedAction.FIX_SEO

    task = SeoOpportunityTask.objects.create(
        source=source,
        title=str(payload.get("title") or "Growth SEO task")[:255],
        rationale=str(payload.get("rationale") or "Proposed by growth agent")[:4000],
        priority=int(payload.get("priority") or 60),
        status=SeoOpportunityTask.Status.OPEN,
        suggested_action=suggested,
        path=str(payload.get("path") or "")[:512],
        keyword_id=payload.get("keyword_id") or None,
        tool_opportunity_id=payload.get("opportunity_id") or None,
    )
    return {"type": "SeoOpportunityTask", "id": task.pk, "status": task.status}


def _queue_tool_spec(payload: dict[str, Any], *, user=None) -> dict[str, Any]:
    from apps.tool_intelligence.models import ToolOpportunity
    from apps.tool_intelligence.services import queue_opportunity

    opp_id = payload.get("opportunity_id")
    if opp_id:
        opp = ToolOpportunity.objects.get(pk=opp_id)
    else:
        slug = slugify(str(payload.get("suggested_slug") or payload.get("title") or "tool"))[
            :120
        ]
        opp, _ = ToolOpportunity.objects.get_or_create(
            suggested_slug=slug or "growth-tool",
            defaults={
                "category_slug": str(payload.get("category_slug") or "ai"),
                "title": str(payload.get("title") or slug)[:255],
                "rationale": str(payload.get("rationale") or "Queued by growth agent"),
                "priority_score": float(payload.get("priority_score") or 50),
                "status": ToolOpportunity.Status.OPEN,
            },
        )
    queued = queue_opportunity(opp, user=user)
    ref: dict[str, Any] = {
        "type": "ToolOpportunity",
        "id": queued.pk,
        "status": queued.status,
    }
    if queued.tool_spec_id:
        ref["tool_spec_id"] = queued.tool_spec_id
        ref["tool_spec_status"] = queued.tool_spec.status if queued.tool_spec else None
    return ref


def _start_autopilot_draft(payload: dict[str, Any]) -> dict[str, Any]:
    """Create AutopilotRun + ContentItem stuck in human_review — never published."""
    from apps.content_factory.models import AutopilotRun, ContentItem

    keyword = str(payload.get("keyword") or "growth topic").strip()
    locale = str(payload.get("locale") or "en")[:10]
    base_slug = slugify(f"growth-{keyword}")[:200] or "growth-draft"
    slug = base_slug
    n = 1
    while ContentItem.objects.filter(slug=slug).exists():
        n += 1
        slug = f"{base_slug}-{n}"[:255]

    item = ContentItem.objects.create(
        title=f"Draft: {keyword}"[:255],
        slug=slug,
        body=(
            f"# {keyword.title()}\n\n"
            "Draft generated by growth agent for human review. "
            "Do not publish until reviewed.\n"
        ),
        content_type="blog",
        status=ContentItem.Status.HUMAN_REVIEW,
        locale=locale,
        meta_title=f"{keyword.title()} | ToolVerse AI"[:255],
        meta_description=f"Human-review draft covering {keyword}."[:500],
    )
    run = AutopilotRun.objects.create(
        keyword_id=payload.get("keyword_id") or None,
        stage="human_review",
        status=AutopilotRun.Status.HUMAN_REVIEW,
        content_item=item,
        quality_score=40.0,
    )
    assert item.status != ContentItem.Status.PUBLISHED
    assert run.status != AutopilotRun.Status.PUBLISHED
    return {
        "type": "AutopilotRun",
        "id": run.pk,
        "status": run.status,
        "content_item_id": item.pk,
        "content_status": item.status,
        "published": False,
    }


def _create_content_draft(payload: dict[str, Any], *, user=None) -> dict[str, Any]:
    from apps.content_factory.models import ContentItem

    keyword = str(payload.get("keyword") or payload.get("title") or "content").strip()
    locale = str(payload.get("locale") or "en")[:10]
    base_slug = slugify(f"draft-{keyword}")[:200] or "content-draft"
    slug = base_slug
    n = 1
    while ContentItem.objects.filter(slug=slug).exists():
        n += 1
        slug = f"{base_slug}-{n}"[:255]

    item = ContentItem.objects.create(
        title=str(payload.get("title") or f"Draft: {keyword}")[:255],
        slug=slug,
        body=str(
            payload.get("body")
            or f"# {keyword.title()}\n\nHuman-review content draft from growth agent.\n"
        ),
        content_type=str(payload.get("content_type") or "blog"),
        status=ContentItem.Status.HUMAN_REVIEW,
        locale=locale,
        created_by=user if getattr(user, "is_authenticated", False) else None,
        meta_title=str(payload.get("meta_title") or keyword)[:255],
        meta_description=str(payload.get("meta_description") or "")[:500],
    )
    assert item.status != ContentItem.Status.PUBLISHED
    return {
        "type": "ContentItem",
        "id": item.pk,
        "status": item.status,
        "slug": item.slug,
        "published": False,
    }
