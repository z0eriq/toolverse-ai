"""SEO Autopilot — scan issues and apply safe SEO field mutations."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.seo_optimizer.models import SeoApplyLog, SeoAutopilotRun, SeoHealthScore, SeoPageIssue

logger = logging.getLogger("toolverse.seo_optimizer")


def _tool_path_slug(path: str) -> str | None:
    """Extract tool slug from paths like /tools/pdf/merge or tools/pdf/merge."""
    cleaned = path.strip().strip("/")
    parts = [p for p in cleaned.split("/") if p]
    if len(parts) >= 3 and parts[0] == "tools":
        return parts[-1]
    if len(parts) == 2 and parts[0] == "tools":
        return parts[1]
    if len(parts) == 1 and parts[0] not in {"tools", "best", "blog"}:
        return parts[0]
    return None


@transaction.atomic
def scan_seo_autopilot() -> SeoAutopilotRun:
    """
    Create SeoPageIssue rows from low health scores, GSC CTR heuristics,
    and missing tool paths as broken_link samples.
    """
    run = SeoAutopilotRun.objects.create(status=SeoAutopilotRun.Status.RUNNING)
    created = 0
    try:
        for score in SeoHealthScore.objects.filter(overall__lt=70).order_by("overall")[:40]:
            issue_type = SeoPageIssue.IssueType.META
            suggestion = f"Improve metadata on {score.path} (health {score.overall:.1f})."
            if score.schema < 50:
                issue_type = SeoPageIssue.IssueType.FAQ
                suggestion = f"Add FAQ schema content for {score.path}."
            elif score.internal_links < 50:
                issue_type = SeoPageIssue.IssueType.INTERNAL_LINK
                suggestion = f"Add internal links on {score.path}."
            elif score.content_quality < 50:
                issue_type = SeoPageIssue.IssueType.FRESHNESS
                suggestion = f"Refresh content on {score.path}."
            SeoPageIssue.objects.create(
                run=run,
                path=score.path,
                issue_type=issue_type,
                severity=(
                    SeoPageIssue.Severity.HIGH
                    if score.overall < 40
                    else SeoPageIssue.Severity.MEDIUM
                ),
                suggestion=suggestion,
                status=SeoPageIssue.Status.OPEN,
                evidence={"overall": score.overall, "source": "seo_health"},
            )
            created += 1

        try:
            from apps.search_console.models import GSCMetricSnapshot

            for snap in (
                GSCMetricSnapshot.objects.filter(impressions__gte=50, ctr__lt=0.02)
                .exclude(page="")
                .order_by("-impressions")[:20]
            ):
                SeoPageIssue.objects.create(
                    run=run,
                    path=snap.page[:512],
                    issue_type=SeoPageIssue.IssueType.CTR,
                    severity=SeoPageIssue.Severity.MEDIUM,
                    suggestion=(
                        f"Improve title/meta CTR for {snap.page} "
                        f"(ctr={snap.ctr:.3f}, impressions={snap.impressions})."
                    ),
                    status=SeoPageIssue.Status.OPEN,
                    evidence={
                        "ctr": snap.ctr,
                        "impressions": snap.impressions,
                        "query": snap.query,
                        "source": "gsc",
                    },
                )
                created += 1
        except Exception as exc:  # noqa: BLE001
            logger.debug("GSC scan skipped: %s", exc)

        try:
            from apps.tools_registry.models import Tool

            existing_slugs = set(Tool.objects.filter(is_active=True).values_list("slug", flat=True))
            sample_missing = [
                "tools/demo/missing-tool-alpha",
                "tools/demo/missing-tool-beta",
            ]
            for path in sample_missing:
                slug = path.rsplit("/", 1)[-1]
                if slug not in existing_slugs:
                    SeoPageIssue.objects.create(
                        run=run,
                        path=path,
                        issue_type=SeoPageIssue.IssueType.BROKEN_LINK,
                        severity=SeoPageIssue.Severity.LOW,
                        suggestion=f"Broken or missing tool path sample: {path}",
                        status=SeoPageIssue.Status.OPEN,
                        evidence={"source": "missing_tool_path", "slug": slug},
                    )
                    created += 1
        except Exception as exc:  # noqa: BLE001
            logger.debug("broken_link samples skipped: %s", exc)

        run.status = SeoAutopilotRun.Status.SUCCESS
        run.issues_created = created
        run.summary = f"Created {created} SEO page issues."
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "status",
                "issues_created",
                "summary",
                "finished_at",
                "updated_at",
            ]
        )
        return run
    except Exception as exc:  # noqa: BLE001
        logger.exception("scan_seo_autopilot failed")
        run.status = SeoAutopilotRun.Status.FAILED
        run.error = str(exc)[:2000]
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at", "updated_at"])
        return run


@transaction.atomic
def apply_page_issue(issue: SeoPageIssue, user=None) -> SeoPageIssue:
    """
    Apply a page issue by mutating Tool or ProgrammaticPage SEO fields when possible.
    Marks the issue applied and writes SeoApplyLog.
    """
    if issue.status != SeoPageIssue.Status.OPEN:
        return issue

    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    note = ""

    tool = _resolve_tool(issue.path)
    page = None if tool else _resolve_programmatic_page(issue.path)

    if tool is not None:
        before = {
            "seo_title": tool.seo_title,
            "seo_description": tool.seo_description,
            "faq": tool.faq,
            "related_slugs": tool.related_slugs,
        }
        if issue.issue_type == SeoPageIssue.IssueType.META:
            title = _localized(tool.seo_title) or _localized(tool.name) or tool.slug
            improved = f"{title} — Free Online Tool | ToolVerse AI"[:120]
            tool.seo_title = {**(tool.seo_title or {}), "en": improved}
            desc = _localized(tool.seo_description) or _localized(tool.description)
            if len(desc) < 80:
                tool.seo_description = {
                    **(tool.seo_description or {}),
                    "en": (
                        f"Use {title} free online. Fast, private, and no signup required "
                        f"on ToolVerse AI."
                    )[:160],
                }
            note = "Updated Tool seo_title/seo_description"
        elif issue.issue_type == SeoPageIssue.IssueType.FAQ:
            if not tool.faq:
                name = _localized(tool.name) or tool.slug
                tool.faq = [
                    {
                        "question": f"What is {name}?",
                        "answer": f"{name} is a free online tool on ToolVerse AI.",
                    },
                    {
                        "question": f"Is {name} free?",
                        "answer": "Yes. Core usage is free in the browser.",
                    },
                ]
                note = "Seeded Tool FAQ"
            else:
                note = "FAQ already present"
        elif issue.issue_type == SeoPageIssue.IssueType.INTERNAL_LINK:
            related = list(tool.related_slugs or [])
            if tool.slug not in related:
                # Keep existing related; add category peers if empty
                from apps.tools_registry.models import Tool as ToolModel

                peers = list(
                    ToolModel.objects.filter(
                        category_id=tool.category_id, is_active=True
                    )
                    .exclude(pk=tool.pk)
                    .values_list("slug", flat=True)[:5]
                )
                tool.related_slugs = list(dict.fromkeys([*related, *peers]))[:12]
                note = "Updated related_slugs"
            else:
                note = "related_slugs unchanged"
        elif issue.issue_type == SeoPageIssue.IssueType.CTR:
            title = _localized(tool.seo_title) or _localized(tool.name) or tool.slug
            tool.seo_title = {
                **(tool.seo_title or {}),
                "en": f"{title} Free — Instant Results"[:120],
            }
            note = "Rewrote title for CTR"
        else:
            note = f"No automated mutation for {issue.issue_type} on tool"
        tool.save()
        after = {
            "seo_title": tool.seo_title,
            "seo_description": tool.seo_description,
            "faq": tool.faq,
            "related_slugs": tool.related_slugs,
        }
    elif page is not None:
        before = {
            "seo_title": page.seo_title,
            "seo_description": page.seo_description,
            "status": page.status,
        }
        if issue.issue_type in {
            SeoPageIssue.IssueType.META,
            SeoPageIssue.IssueType.CTR,
            SeoPageIssue.IssueType.FRESHNESS,
        }:
            title = _localized(page.seo_title) or _localized(page.title) or page.slug
            page.seo_title = {
                **(page.seo_title or {}),
                "en": f"{title} | ToolVerse AI"[:120],
            }
            desc = _localized(page.seo_description) or _localized(page.description)
            if len(desc) < 80:
                page.seo_description = {
                    **(page.seo_description or {}),
                    "en": f"Explore {title} with free online tools on ToolVerse AI."[:160],
                }
            # Never auto-publish
            page.save()
            note = "Updated ProgrammaticPage SEO fields (status unchanged)"
        else:
            note = f"No automated mutation for {issue.issue_type} on programmatic page"
        after = {
            "seo_title": page.seo_title,
            "seo_description": page.seo_description,
            "status": page.status,
        }
    else:
        note = "No Tool or ProgrammaticPage matched; marked applied without mutation"

    SeoApplyLog.objects.create(
        issue=issue,
        applied_by=user if getattr(user, "is_authenticated", False) else None,
        before=before,
        after=after,
        note=note,
    )
    issue.status = SeoPageIssue.Status.APPLIED
    issue.save(update_fields=["status", "updated_at"])
    return issue


def _localized(mapping: Any) -> str:
    if isinstance(mapping, dict):
        return str(mapping.get("en") or next(iter(mapping.values()), "") or "")
    return str(mapping or "")


def _resolve_tool(path: str):
    from apps.tools_registry.models import Tool

    slug = _tool_path_slug(path)
    if not slug:
        # Also try last path segment
        parts = [p for p in path.strip("/").split("/") if p]
        slug = parts[-1] if parts else None
    if not slug:
        return None
    return Tool.objects.filter(slug=slug).select_related("category").first()


def _resolve_programmatic_page(path: str):
    from apps.programmatic_seo.models import ProgrammaticPage

    cleaned = path.strip().strip("/")
    return ProgrammaticPage.objects.filter(slug=cleaned).first() or ProgrammaticPage.objects.filter(
        slug=cleaned.replace(" ", "-")
    ).first()
