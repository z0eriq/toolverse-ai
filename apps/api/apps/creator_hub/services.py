from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils.text import slugify

from apps.creator_hub.models import CreatorProfile, CreatorSubmission
from apps.tool_factory.models import ToolSpec

logger = logging.getLogger("toolverse.creator_hub")


def get_or_create_creator_profile(user) -> CreatorProfile:
    profile, _ = CreatorProfile.objects.get_or_create(
        user=user,
        defaults={"display_name": user.name or user.email.split("@")[0]},
    )
    return profile


@transaction.atomic
def submit_for_review(submission: CreatorSubmission) -> CreatorSubmission:
    if submission.status not in {
        CreatorSubmission.Status.DRAFT,
        CreatorSubmission.Status.REJECTED,
    }:
        raise ValueError("Only draft or rejected submissions can be submitted")
    submission.status = CreatorSubmission.Status.PENDING
    submission.save(update_fields=["status", "updated_at"])
    return submission


@transaction.atomic
def approve_submission(
    submission: CreatorSubmission,
    *,
    reviewer=None,
    notes: str = "",
) -> CreatorSubmission:
    submission.status = CreatorSubmission.Status.APPROVED
    if notes:
        submission.reviewer_notes = notes

    if submission.type == CreatorSubmission.Type.TOOL and submission.tool_spec_id is None:
        payload: dict[str, Any] = submission.payload if isinstance(submission.payload, dict) else {}
        raw_slug = payload.get("slug") or payload.get("name") or f"creator-tool-{submission.pk}"
        slug = slugify(str(raw_slug))[:120] or f"creator-tool-{submission.pk}"
        base = slug
        n = 1
        while ToolSpec.objects.filter(slug=slug).exists():
            n += 1
            slug = f"{base}-{n}"[:120]

        name = payload.get("name")
        if isinstance(name, str):
            name = {"en": name}
        elif not isinstance(name, dict):
            name = {"en": slug}

        description = payload.get("description")
        if isinstance(description, str):
            description = {"en": description}
        elif not isinstance(description, dict):
            description = {"en": ""}

        submission.tool_spec = ToolSpec.objects.create(
            slug=slug,
            category_slug=payload.get("category_slug") or "ai",
            name=name,
            description=description,
            ui_schema=payload.get("ui_schema") or {},
            pipeline=payload.get("pipeline") or [],
            seo=payload.get("seo") or {},
            faq=payload.get("faq") or [],
            howto=payload.get("howto") or [],
            capabilities=payload.get("capabilities") or [],
            recipe=payload.get("recipe") or ToolSpec.Recipe.GENERIC,
            status=ToolSpec.Status.DRAFT,
            created_by=reviewer or submission.creator.user,
        )

    if submission.type == CreatorSubmission.Type.TEMPLATE:
        try:
            from apps.workflows.models import WorkflowTemplate

            payload = submission.payload if isinstance(submission.payload, dict) else {}
            tpl_slug = slugify(str(payload.get("slug") or f"creator-tpl-{submission.pk}"))[:120]
            WorkflowTemplate.objects.update_or_create(
                slug=tpl_slug,
                defaults={
                    "name": payload.get("name") or tpl_slug,
                    "description": payload.get("description") or "",
                    "steps": payload.get("steps") or [],
                    "category": payload.get("category") or "creator",
                    "is_public": False,
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.info("template approve side-effect skipped: %s", exc)

    submission.save()
    return submission


@transaction.atomic
def reject_submission(submission: CreatorSubmission, *, notes: str = "") -> CreatorSubmission:
    submission.status = CreatorSubmission.Status.REJECTED
    if notes:
        submission.reviewer_notes = notes
    submission.save(update_fields=["status", "reviewer_notes", "updated_at"])
    return submission


def _period_key(period_start, period_end) -> str:
    return f"{period_start.isoformat()}:{period_end.isoformat()}"


def rollup_creator_usage(period_start, period_end) -> dict:
    """
    Aggregate AnalyticsEvent tool runs for approved creator ToolSpecs into CreatorUsageStat.
    """
    from datetime import datetime

    from django.db.models import Q
    from django.utils import timezone

    from apps.creator_hub.models import CreatorSubmission, CreatorUsageStat

    if isinstance(period_start, datetime):
        start_dt = period_start
        period_start_d = period_start.date()
    else:
        start_dt = timezone.make_aware(datetime.combine(period_start, datetime.min.time()))
        period_start_d = period_start
    if isinstance(period_end, datetime):
        end_dt = period_end
        period_end_d = period_end.date()
    else:
        end_dt = timezone.make_aware(datetime.combine(period_end, datetime.max.time()))
        period_end_d = period_end

    period = _period_key(period_start_d, period_end_d)
    created = updated = 0

    approved = CreatorSubmission.objects.filter(
        status=CreatorSubmission.Status.APPROVED,
        type=CreatorSubmission.Type.TOOL,
        tool_spec__isnull=False,
    ).select_related("tool_spec", "creator")

    try:
        from apps.analytics.models import AnalyticsEvent
    except Exception:  # noqa: BLE001
        AnalyticsEvent = None  # type: ignore[assignment]

    for submission in approved:
        slug = submission.tool_spec.slug if submission.tool_spec_id else ""
        runs = 0
        unique_users = 0
        if AnalyticsEvent is not None and slug:
            qs = AnalyticsEvent.objects.filter(
                created_at__gte=start_dt,
                created_at__lte=end_dt,
                name__in=("use", "tool_use", "tool_run", "run", "tool_execution"),
            ).filter(
                Q(tool_id=slug) | Q(tool_id__endswith=f"/{slug}") | Q(tool_id__contains=slug)
            )
            runs = qs.count()
            unique_users = qs.exclude(user_id=None).values("user_id").distinct().count()
            if unique_users == 0:
                unique_users = qs.exclude(session_id="").values("session_id").distinct().count()

        _, was_created = CreatorUsageStat.objects.update_or_create(
            submission=submission,
            period=period,
            defaults={
                "tool_slug": slug,
                "runs": runs,
                "unique_users": unique_users,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {"created": created, "updated": updated, "period": period}


def accrue_revenue_shares(period_start=None, period_end=None, *, period: str | None = None) -> dict:
    """
    Create/update CreatorRevenueShareStub from usage stats.
    Default share_bps=7000; amount_cents = runs * share_bps/10000 (stub cents).
    """
    from datetime import datetime

    from apps.creator_hub.models import CreatorRevenueShareStub, CreatorUsageStat

    qs = CreatorUsageStat.objects.select_related("submission", "submission__creator")
    if period:
        qs = qs.filter(period=period)
    elif period_start is not None and period_end is not None:
        ps = period_start.date() if isinstance(period_start, datetime) else period_start
        pe = period_end.date() if isinstance(period_end, datetime) else period_end
        qs = qs.filter(period=_period_key(ps, pe))

    accrued = 0
    for stat in qs:
        if not stat.submission_id or not stat.submission.creator_id:
            continue
        creator = stat.submission.creator
        share_bps = 7000
        gross = int(stat.runs or 0)
        amount_cents = max(0, int(gross * share_bps / 10000))
        CreatorRevenueShareStub.objects.update_or_create(
            creator=creator,
            period=stat.period,
            defaults={
                "amount_cents": amount_cents,
                "share_bps": share_bps,
                "status": CreatorRevenueShareStub.Status.ACCRUED,
            },
        )
        accrued += 1
    return {"accrued": accrued}
