from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.seo_optimizer.models import SeoHealthScore
from apps.seo_optimizer.services import _normalize_path, _tool_from_path

logger = logging.getLogger("toolverse.seo_optimizer")

WEIGHTS = {
    "metadata": 0.20,
    "schema": 0.15,
    "internal_links": 0.15,
    "content_quality": 0.20,
    "keyword_coverage": 0.15,
    "performance": 0.15,
}


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _score_metadata(tool) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    if tool is None:
        recs.append(
            {
                "dimension": "metadata",
                "severity": "medium",
                "suggestion": "Associate this path with a tool and set SEO title/description.",
            }
        )
        return 40.0, recs

    title = ""
    if isinstance(tool.seo_title, dict):
        title = str(tool.seo_title.get("en") or next(iter(tool.seo_title.values()), "") or "")
    elif tool.seo_title:
        title = str(tool.seo_title)

    meta = ""
    if isinstance(tool.seo_description, dict):
        meta = str(
            tool.seo_description.get("en") or next(iter(tool.seo_description.values()), "") or ""
        )

    score = 100.0
    if not title:
        score -= 40
        recs.append(
            {
                "dimension": "metadata",
                "severity": "high",
                "suggestion": "Add an SEO title (50–60 characters).",
            }
        )
    elif len(title) < 30 or len(title) > 65:
        score -= 20
        recs.append(
            {
                "dimension": "metadata",
                "severity": "medium",
                "suggestion": f"Tune title length (current {len(title)}; ideal 50–60).",
            }
        )

    if not meta or len(meta) < 70:
        score -= 25
        recs.append(
            {
                "dimension": "metadata",
                "severity": "medium",
                "suggestion": "Expand meta description to ~120–160 characters.",
            }
        )
    elif len(meta) > 165:
        score -= 10
        recs.append(
            {
                "dimension": "metadata",
                "severity": "low",
                "suggestion": "Shorten meta description to avoid SERP truncation.",
            }
        )

    return _clamp(score), recs


def _score_schema(tool) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    if tool is None:
        return 35.0, [
            {
                "dimension": "schema",
                "severity": "low",
                "suggestion": "Add FAQ / SoftwareApplication schema for this path.",
            }
        ]

    faq = tool.faq if isinstance(tool.faq, list) else []
    score = 50.0
    if len(faq) >= 3:
        score = 95.0
    elif len(faq) >= 2:
        score = 80.0
    elif len(faq) == 1:
        score = 60.0
        recs.append(
            {
                "dimension": "schema",
                "severity": "medium",
                "suggestion": "Add 2–3 FAQ items to improve FAQ rich-result eligibility.",
            }
        )
    else:
        score = 40.0
        recs.append(
            {
                "dimension": "schema",
                "severity": "high",
                "suggestion": "Add FAQ content to enable FAQ schema markup.",
            }
        )
    return _clamp(score), recs


def _score_internal_links(tool) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    if tool is None:
        return 30.0, [
            {
                "dimension": "internal_links",
                "severity": "medium",
                "suggestion": "Add internal links from related tools and hubs.",
            }
        ]

    related = tool.related_slugs if isinstance(tool.related_slugs, list) else []
    count = len(related)
    if count >= 4:
        score = 95.0
    elif count >= 2:
        score = 75.0
    elif count == 1:
        score = 55.0
        recs.append(
            {
                "dimension": "internal_links",
                "severity": "low",
                "suggestion": "Add more related tool links for topical crawl paths.",
            }
        )
    else:
        score = 35.0
        recs.append(
            {
                "dimension": "internal_links",
                "severity": "medium",
                "suggestion": "Add related tool slugs to improve internal linking.",
            }
        )
    return _clamp(score), recs


def _score_content(tool, path: str) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    if tool is None:
        # Programmatic / content pages without a tool
        try:
            from apps.programmatic_seo.models import ProgrammaticPage

            slug = path.strip("/")
            page = ProgrammaticPage.objects.filter(slug=slug).first()
            if page:
                body = page.body if isinstance(page.body, dict) else {}
                text = " ".join(str(v) for v in body.values()) if body else ""
                words = len(text.split())
                if words >= 400:
                    return 85.0, recs
                if words >= 150:
                    return 65.0, recs
                recs.append(
                    {
                        "dimension": "content_quality",
                        "severity": "medium",
                        "suggestion": "Expand programmatic page body for better topical depth.",
                    }
                )
                return 45.0, recs
        except Exception:  # noqa: BLE001
            pass
        return 40.0, [
            {
                "dimension": "content_quality",
                "severity": "medium",
                "suggestion": "Add structured content for this path.",
            }
        ]

    desc = ""
    if isinstance(tool.description, dict):
        desc = str(tool.description.get("en") or next(iter(tool.description.values()), "") or "")
    howto = tool.howto_steps if isinstance(tool.howto_steps, list) else []
    score = 50.0
    if len(desc) >= 120:
        score += 25
    elif len(desc) >= 40:
        score += 10
    else:
        recs.append(
            {
                "dimension": "content_quality",
                "severity": "medium",
                "suggestion": "Expand the tool description for richer on-page content.",
            }
        )
    if len(howto) >= 3:
        score += 20
    elif len(howto) >= 1:
        score += 10
    else:
        recs.append(
            {
                "dimension": "content_quality",
                "severity": "low",
                "suggestion": "Add how-to steps to improve content quality signals.",
            }
        )
    return _clamp(score), recs


def _score_keywords(path: str, tool) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    try:
        from apps.keywords.models import KeywordOpportunity

        flat: list[str] = []
        for part in [p for p in path.split("/") if p]:
            flat.append(part.lower().replace("-", " "))
        if tool is not None:
            flat.append(tool.slug.lower().replace("-", " "))
            if isinstance(tool.name, dict):
                for v in tool.name.values():
                    flat.extend(str(v).lower().split())
            keywords = tool.seo_keywords if isinstance(tool.seo_keywords, list) else []
            flat.extend(str(k).lower() for k in keywords)

        if not flat:
            return 30.0, [
                {
                    "dimension": "keyword_coverage",
                    "severity": "low",
                    "suggestion": "Target keywords from KeywordOpportunity for this path.",
                }
            ]

        matched = 0
        for token in flat[:12]:
            if len(token) < 3:
                continue
            if KeywordOpportunity.objects.filter(keyword__icontains=token).exists():
                matched += 1
        if matched >= 3:
            score = 90.0
        elif matched >= 1:
            score = 65.0
        else:
            score = 35.0
            recs.append(
                {
                    "dimension": "keyword_coverage",
                    "severity": "medium",
                    "suggestion": "Align page keywords with open KeywordOpportunity rows.",
                }
            )
        return _clamp(score), recs
    except Exception as exc:  # noqa: BLE001
        logger.debug("keyword scoring skipped: %s", exc)
        return 50.0, recs


def _score_performance(perf: float | dict[str, Any] | None) -> tuple[float, list[dict[str, Any]]]:
    recs: list[dict[str, Any]] = []
    if perf is None:
        return 70.0, recs
    if isinstance(perf, (int, float)):
        return _clamp(float(perf)), recs
    if isinstance(perf, dict):
        if "score" in perf:
            return _clamp(float(perf["score"])), recs
        # CWV-ish composite
        lcp = float(perf.get("lcp_ms") or 2500)
        cls = float(perf.get("cls") or 0.1)
        inp = float(perf.get("inp_ms") or 200)
        score = 100.0
        if lcp > 4000:
            score -= 35
        elif lcp > 2500:
            score -= 15
        if cls > 0.25:
            score -= 25
        elif cls > 0.1:
            score -= 10
        if inp > 500:
            score -= 20
        elif inp > 200:
            score -= 8
        if score < 80:
            recs.append(
                {
                    "dimension": "performance",
                    "severity": "medium",
                    "suggestion": "Improve Core Web Vitals (LCP/CLS/INP) for this path.",
                }
            )
        return _clamp(score), recs
    return 70.0, recs


@transaction.atomic
def compute_seo_health(
    path: str,
    perf: float | dict[str, Any] | None = None,
) -> SeoHealthScore:
    """Compute and upsert SeoHealthScore for a path using deterministic heuristics."""
    normalized = _normalize_path(path)
    tool = _tool_from_path(normalized)

    metadata, r1 = _score_metadata(tool)
    schema, r2 = _score_schema(tool)
    internal_links, r3 = _score_internal_links(tool)
    content_quality, r4 = _score_content(tool, normalized)
    keyword_coverage, r5 = _score_keywords(normalized, tool)
    performance, r6 = _score_performance(perf)

    overall = _clamp(
        metadata * WEIGHTS["metadata"]
        + schema * WEIGHTS["schema"]
        + internal_links * WEIGHTS["internal_links"]
        + content_quality * WEIGHTS["content_quality"]
        + keyword_coverage * WEIGHTS["keyword_coverage"]
        + performance * WEIGHTS["performance"]
    )
    recommendations = r1 + r2 + r3 + r4 + r5 + r6
    now = timezone.now()

    score, _ = SeoHealthScore.objects.update_or_create(
        path=normalized,
        defaults={
            "metadata": metadata,
            "schema": schema,
            "internal_links": internal_links,
            "content_quality": content_quality,
            "keyword_coverage": keyword_coverage,
            "performance": performance,
            "overall": overall,
            "recommendations": recommendations,
            "analyzed_at": now,
        },
    )
    return score


def recompute_all_seo_health(*, tool_limit: int = 50) -> dict[str, Any]:
    """Score published programmatic pages and top tools."""
    paths: list[str] = []
    try:
        from apps.programmatic_seo.models import ProgrammaticPage

        for page in ProgrammaticPage.objects.filter(
            status=ProgrammaticPage.Status.PUBLISHED
        ).only("slug"):
            paths.append("/" + page.slug.strip("/"))
    except Exception as exc:  # noqa: BLE001
        logger.info("programmatic paths skipped: %s", exc)

    try:
        from apps.tools_registry.models import Tool

        for tool in Tool.objects.filter(is_active=True).select_related("category")[:tool_limit]:
            cat = tool.category.slug if tool.category_id else "tools"
            paths.append(f"/tools/{cat}/{tool.slug}")
    except Exception as exc:  # noqa: BLE001
        logger.info("tool paths skipped: %s", exc)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for p in paths:
        n = _normalize_path(p)
        if n not in seen:
            seen.add(n)
            unique.append(n)

    computed = 0
    errors = 0
    for path in unique:
        try:
            compute_seo_health(path)
            computed += 1
        except Exception:  # noqa: BLE001
            logger.exception("compute_seo_health failed for %s", path)
            errors += 1

    return {"paths": len(unique), "computed": computed, "errors": errors}
