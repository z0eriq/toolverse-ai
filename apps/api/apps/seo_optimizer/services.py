from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction

from apps.seo_optimizer.models import SeoRecommendation
from apps.tools_registry.models import Tool

logger = logging.getLogger("toolverse.seo_optimizer")


def _normalize_path(path: str) -> str:
    raw = (path or "").strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        raw = urlparse(raw).path or "/"
    if not raw.startswith("/"):
        raw = "/" + raw
    return raw.rstrip("/") or "/"


def _tool_from_path(path: str) -> Tool | None:
    # /tools/{category}/{slug} or /{locale}/tools/{category}/{slug}
    parts = [p for p in path.split("/") if p]
    if "tools" in parts:
        idx = parts.index("tools")
        if len(parts) > idx + 2:
            slug = parts[idx + 2]
            return Tool.objects.filter(slug=slug, is_active=True).first()
    if len(parts) == 1:
        return Tool.objects.filter(slug=parts[0], is_active=True).first()
    return None


def _gsc_evidence(path: str) -> dict[str, Any]:
    try:
        from django.db.models import Avg, Sum

        from apps.search_console.models import GSCMetricSnapshot

        qs = GSCMetricSnapshot.objects.filter(page__icontains=path)
        agg = qs.aggregate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_ctr=Avg("ctr"),
        )
        return {
            "gsc_clicks": agg.get("clicks") or 0,
            "gsc_impressions": agg.get("impressions") or 0,
            "gsc_avg_ctr": agg.get("avg_ctr") or 0,
            "gsc_rows": qs.count(),
        }
    except Exception:  # noqa: BLE001
        return {}


def _heuristic_recs(path: str, tool: Tool | None) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    evidence = _gsc_evidence(path)

    if tool is None:
        recs.append(
            {
                "type": SeoRecommendation.Type.CONTENT,
                "severity": SeoRecommendation.Severity.LOW,
                "suggestion": "Add structured content and internal links for this path.",
                "rationale": "No matching Tool was found for the analyzed path.",
                "evidence": evidence,
            }
        )
        return recs

    title = ""
    if isinstance(tool.seo_title, dict):
        title = str(tool.seo_title.get("en") or next(iter(tool.seo_title.values()), "") or "")
    elif tool.seo_title:
        title = str(tool.seo_title)

    if not title:
        recs.append(
            {
                "type": SeoRecommendation.Type.TITLE,
                "severity": SeoRecommendation.Severity.HIGH,
                "suggestion": f"Add an SEO title for {tool.slug} (aim for 50–60 characters).",
                "rationale": "Missing seo_title reduces click-through from search results.",
                "evidence": evidence,
            }
        )
    elif len(title) < 30 or len(title) > 65:
        recs.append(
            {
                "type": SeoRecommendation.Type.TITLE,
                "severity": SeoRecommendation.Severity.MEDIUM,
                "suggestion": f"Tune title length for {tool.slug} (current {len(title)} chars; ideal 50–60).",
                "rationale": "Title length outside the typical SERP display range.",
                "evidence": {**evidence, "title_length": len(title)},
            }
        )

    meta = ""
    if isinstance(tool.seo_description, dict):
        meta = str(tool.seo_description.get("en") or next(iter(tool.seo_description.values()), "") or "")
    if not meta or len(meta) < 70:
        recs.append(
            {
                "type": SeoRecommendation.Type.META,
                "severity": SeoRecommendation.Severity.MEDIUM,
                "suggestion": f"Expand the meta description for {tool.slug} to ~120–160 characters.",
                "rationale": "Short or missing meta descriptions hurt SERP snippets.",
                "evidence": {**evidence, "meta_length": len(meta)},
            }
        )

    faq = tool.faq if isinstance(tool.faq, list) else []
    if len(faq) < 2:
        recs.append(
            {
                "type": SeoRecommendation.Type.FAQ,
                "severity": SeoRecommendation.Severity.HIGH,
                "suggestion": f"Add at least 2–3 FAQ items for {tool.slug} to enable FAQ rich results.",
                "rationale": "Missing FAQ content reduces eligibility for FAQ schema.",
                "evidence": {**evidence, "faq_count": len(faq)},
            }
        )

    related = tool.related_slugs if isinstance(tool.related_slugs, list) else []
    if len(related) < 2:
        recs.append(
            {
                "type": SeoRecommendation.Type.INTERNAL_LINK,
                "severity": SeoRecommendation.Severity.LOW,
                "suggestion": f"Add related tool slugs on {tool.slug} to improve internal linking.",
                "rationale": "Sparse related tools reduce topical crawl paths.",
                "evidence": {**evidence, "related_count": len(related)},
            }
        )

    return recs


def _maybe_ai_recs(path: str, tool: Tool | None) -> list[dict[str, Any]]:
    has_key = any(
        getattr(settings, key, "")
        for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY")
    )
    if not has_key:
        return []

    try:
        from apps.ai_providers.router import get_ai_router

        name = (tool.name or {}).get("en") if tool and isinstance(tool.name, dict) else path
        result = get_ai_router().complete(
            [
                {
                    "role": "system",
                    "content": "You are an SEO advisor for ToolVerse AI. Reply with one short actionable tip.",
                },
                {
                    "role": "user",
                    "content": f"Suggest one SEO improvement for path {path} tool={name}",
                },
            ],
            temperature=0.3,
            max_tokens=200,
            tool_id="seo_optimizer",
        )
        tip = (result.content or "").strip()
        if not tip:
            return []
        return [
            {
                "type": SeoRecommendation.Type.CONTENT,
                "severity": SeoRecommendation.Severity.LOW,
                "suggestion": tip[:2000],
                "rationale": "AI-assisted recommendation",
                "evidence": {"provider": result.provider, "model": result.model},
            }
        ]
    except Exception as exc:  # noqa: BLE001
        logger.info("AI SEO recommendation skipped: %s", exc)
        return []


@transaction.atomic
def analyze_page(path: str) -> list[SeoRecommendation]:
    """Create heuristic (and optional AI) SEO recommendations for a path."""
    normalized = _normalize_path(path)
    tool = _tool_from_path(normalized)
    payloads = _heuristic_recs(normalized, tool) + _maybe_ai_recs(normalized, tool)

    created: list[SeoRecommendation] = []
    for item in payloads:
        rec = SeoRecommendation.objects.create(
            path=normalized,
            tool=tool,
            type=item["type"],
            severity=item["severity"],
            suggestion=item["suggestion"],
            rationale=item.get("rationale") or "",
            status=SeoRecommendation.Status.OPEN,
            evidence=item.get("evidence") or {},
        )
        created.append(rec)
    return created


def generate_seo_opportunity_tasks() -> dict[str, Any]:
    """
    Generate actionable SEO opportunity tasks from keywords, health scores,
    and open tool opportunities. Idempotent on title+source for open tasks.
    """
    from apps.seo_optimizer.models import SeoHealthScore, SeoOpportunityTask

    created = 0
    seen_keys: set[str] = set()

    def _upsert(
        *,
        source: str,
        title: str,
        rationale: str,
        priority: int,
        suggested_action: str,
        path: str = "",
        keyword=None,
        tool_opportunity=None,
    ) -> None:
        nonlocal created
        key = f"{source}:{title}"
        if key in seen_keys:
            return
        seen_keys.add(key)
        existing = SeoOpportunityTask.objects.filter(
            source=source,
            title=title,
            status__in=(
                SeoOpportunityTask.Status.OPEN,
                SeoOpportunityTask.Status.IN_PROGRESS,
            ),
        ).first()
        if existing:
            return
        SeoOpportunityTask.objects.create(
            source=source,
            title=title,
            rationale=rationale,
            priority=priority,
            status=SeoOpportunityTask.Status.OPEN,
            suggested_action=suggested_action,
            path=path or "",
            keyword=keyword,
            tool_opportunity=tool_opportunity,
        )
        created += 1

    try:
        from apps.keywords.models import KeywordOpportunity

        for kw in KeywordOpportunity.objects.order_by("-priority_score")[:25]:
            _upsert(
                source=SeoOpportunityTask.Source.KEYWORD,
                title=f"Capture keyword “{kw.keyword}”",
                rationale=(
                    f"Priority {kw.priority_score:.1f}, impressions={kw.impressions}, "
                    f"volume={kw.search_volume}, locale={kw.locale}."
                ),
                priority=int(min(99, max(40, kw.priority_score or 50))),
                suggested_action=(
                    SeoOpportunityTask.SuggestedAction.CREATE_TOOL
                    if kw.suggested_tool_slug
                    else SeoOpportunityTask.SuggestedAction.WRITE_CONTENT
                ),
                keyword=kw,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("keyword tasks skipped: %s", exc)

    try:
        for hs in SeoHealthScore.objects.filter(overall__lt=70).order_by("overall")[:20]:
            _upsert(
                source=SeoOpportunityTask.Source.HEALTH,
                title=f"Improve SEO health for {hs.path}",
                rationale=f"Overall health {hs.overall:.1f}. Fix metadata, schema, and content.",
                priority=int(min(95, max(45, 100 - hs.overall))),
                suggested_action=SeoOpportunityTask.SuggestedAction.FIX_SEO,
                path=hs.path,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("health tasks skipped: %s", exc)

    try:
        from apps.tool_intelligence.models import ToolOpportunity

        for opp in ToolOpportunity.objects.filter(
            status=ToolOpportunity.Status.OPEN
        ).order_by("-priority_score")[:15]:
            _upsert(
                source=SeoOpportunityTask.Source.OPPORTUNITY,
                title=f"Build tool opportunity: {opp.title}",
                rationale=opp.rationale or f"Open opportunity {opp.suggested_slug}",
                priority=int(min(99, max(50, opp.priority_score or 60))),
                suggested_action=SeoOpportunityTask.SuggestedAction.CREATE_TOOL,
                tool_opportunity=opp,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("opportunity tasks skipped: %s", exc)

    try:
        from django.db.models import Sum

        from apps.search_console.models import GSCMetricSnapshot

        rows = (
            GSCMetricSnapshot.objects.exclude(query="")
            .values("query")
            .annotate(impr=Sum("impressions"), clk=Sum("clicks"))
            .order_by("-impr")[:15]
        )
        for row in rows:
            query = row["query"]
            impr = int(row["impr"] or 0)
            clk = int(row["clk"] or 0)
            if impr < 10:
                continue
            ctr = (clk / impr) if impr else 0
            if ctr > 0.05:
                continue
            _upsert(
                source=SeoOpportunityTask.Source.GSC,
                title=f"Improve CTR for “{query}”",
                rationale=f"GSC impressions={impr}, clicks={clk}, CTR={ctr:.3f}.",
                priority=70,
                suggested_action=SeoOpportunityTask.SuggestedAction.FIX_SEO,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("gsc tasks skipped: %s", exc)

    logger.info("generate_seo_opportunity_tasks created=%s", created)
    return {"created": created, "total": SeoOpportunityTask.objects.count()}
