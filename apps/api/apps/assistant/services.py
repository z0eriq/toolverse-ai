from __future__ import annotations

import json
import logging
import re
from typing import Any

from django.db.models import Q

from apps.ai_providers.base import AIProviderError
from apps.ai_providers.router import get_ai_router
from apps.assistant.models import AssistantSession
from apps.tools_registry.models import Tool

logger = logging.getLogger("toolverse.assistant")

INTENT_CTA: dict[str, dict[str, str]] = {
    "premium_upsell": {"label": "Upgrade to Premium", "href": "/pricing"},
    "enterprise": {"label": "Talk to sales", "href": "/enterprise"},
    "billing": {"label": "Manage billing", "href": "/pricing"},
    "tool_help": {"label": "Browse tools", "href": "/tools"},
}


def detect_intent(message: str) -> str | None:
    """Detect premium_upsell|enterprise|billing|tool_help from message keywords."""
    text = (message or "").lower()
    if any(
        k in text
        for k in (
            "upgrade to premium",
            "go premium",
            "premium plan",
            "upgrade premium",
            "get premium",
            "pro plan",
            "upgrade to pro",
        )
    ):
        return "premium_upsell"
    if any(k in text for k in ("enterprise", "team plan", "company plan", "for business")):
        return "enterprise"
    if any(k in text for k in ("billing", "invoice", "payment", "subscription", "charge me")):
        return "billing"
    if any(
        k in text
        for k in ("how do i use", "how to use", "help with tool", "tool help", "which tool")
    ):
        return "tool_help"
    if "upgrade" in text and ("premium" in text or "pro" in text):
        return "premium_upsell"
    return None


def _localized(mapping: Any, locale: str = "en") -> str:
    if isinstance(mapping, dict):
        return str(mapping.get(locale) or mapping.get("en") or next(iter(mapping.values()), ""))
    return str(mapping or "")


def search_candidate_tools(query: str, limit: int = 12) -> list[Tool]:
    q = (query or "").strip().lower()
    if not q:
        return list(
            Tool.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-usage_count")[:limit]
        )
    tokens = [t for t in re.split(r"\W+", q) if len(t) >= 2][:8]
    qs = Tool.objects.filter(is_active=True).select_related("category")
    if tokens:
        filt = Q()
        for token in tokens:
            filt |= Q(search_document__icontains=token)
        qs = qs.filter(filt)
    else:
        qs = qs.filter(search_document__icontains=q)
    return list(qs.order_by("-usage_count")[:limit])


def recommend_tools(
    message: str,
    *,
    user=None,
    session: AssistantSession | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    candidates = search_candidate_tools(message, limit=12)
    catalog = [
        {
            "slug": t.slug,
            "category": t.category.slug if t.category_id else "",
            "name": _localized(t.name, locale),
            "description": _localized(t.description, locale)[:200],
            "tool_id": t.tool_id,
        }
        for t in candidates
    ]

    system = (
        "You are ToolVerse AI assistant. Help users find the right free online tools. "
        "Reply with a short helpful message and recommend up to 5 tools from the catalog. "
        "Respond ONLY with valid JSON: "
        '{"reply":"...","recommended":[{"slug":"...","category":"...","name":"...","reason":"..."}]}'
    )
    user_prompt = (
        f"User message: {message}\n\n"
        f"Available tools catalog (JSON):\n{json.dumps(catalog, ensure_ascii=False)}"
    )

    recommended: list[dict[str, str]] = []
    reply = ""

    try:
        result = get_ai_router().complete(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
            user=user,
            tool_id="assistant",
        )
        raw = (result.content or "").strip()
        # Extract JSON object if wrapped in fences
        match = re.search(r"\{[\s\S]*\}", raw)
        payload = json.loads(match.group(0) if match else raw)
        reply = str(payload.get("reply") or "").strip()
        for item in payload.get("recommended") or []:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("slug") or "").strip()
            if not slug:
                continue
            recommended.append(
                {
                    "slug": slug,
                    "category": str(item.get("category") or ""),
                    "name": str(item.get("name") or slug),
                    "reason": str(item.get("reason") or ""),
                }
            )
    except (AIProviderError, json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.info("Assistant AI fallback: %s", exc)
        reply = (
            "Here are tools that match your request. "
            "Pick one below to get started — all free on ToolVerse AI."
        )
        for t in candidates[:5]:
            recommended.append(
                {
                    "slug": t.slug,
                    "category": t.category.slug if t.category_id else "",
                    "name": _localized(t.name, locale),
                    "reason": "Matches your search keywords",
                }
            )

    # Prefer catalog names/categories when slug matches
    by_slug = {t.slug: t for t in candidates}
    normalized: list[dict[str, str]] = []
    for item in recommended[:5]:
        tool = by_slug.get(item["slug"])
        if tool:
            item["category"] = tool.category.slug if tool.category_id else item["category"]
            item["name"] = _localized(tool.name, locale) or item["name"]
            normalized.append(item)
        else:
            # Keep AI suggestions that might still exist in DB
            exists = (
                Tool.objects.filter(slug=item["slug"], is_active=True)
                .select_related("category")
                .first()
            )
            if exists:
                item["category"] = exists.category.slug
                item["name"] = _localized(exists.name, locale)
                normalized.append(item)

    if session is not None:
        history = list(session.messages or [])
        history.append({"role": "user", "content": message})
        history.append(
            {
                "role": "assistant",
                "content": reply,
                "recommended": normalized,
            }
        )
        session.messages = history[-40:]
        session.save(update_fields=["messages", "updated_at"])

    intent = detect_intent(message)
    meta: dict[str, Any] = {}
    if intent:
        meta["intent"] = intent
        cta = INTENT_CTA.get(intent)
        if cta:
            meta["suggested_cta"] = cta

    return {"reply": reply, "recommended_tools": normalized, "meta": meta}
