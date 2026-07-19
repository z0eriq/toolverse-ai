"""First-1000 tools expansion: queue draft ToolSpec rows from catalog templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils.text import slugify

from apps.tool_factory.models import ToolSpec

CATALOG_PATH = Path(__file__).resolve().parent / "fixtures" / "expansion_catalog.json"

_DEFAULT_UI = {
    "fields": [
        {"name": "input", "type": "textarea", "label": {"en": "Input"}},
    ]
}
_DEFAULT_PIPELINE = [
    {"type": "transform", "op": "identity", "source": "input.input", "target": "output"},
]


def load_expansion_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def iter_catalog_candidates(category: str, *, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Expand category templates into candidate tool drafts.
    Capacity is structural (slug patterns × actions), not full implementations.
    """
    catalog = load_expansion_catalog()
    categories = catalog.get("categories") or {}
    if category not in categories:
        valid = ", ".join(sorted(categories))
        raise ValueError(f"Unknown category '{category}'. Choose from: {valid}")

    cat = categories[category]
    recipe = cat.get("recipe") or ToolSpec.Recipe.GENERIC
    category_slug = cat.get("category_slug") or category
    out: list[dict[str, Any]] = []

    for tmpl in cat.get("templates") or []:
        pattern = tmpl.get("slug_pattern") or "{action}"
        name_pattern = tmpl.get("name_pattern") or "{Action}"
        desc_pattern = tmpl.get("description_pattern") or "{action}"
        for action in tmpl.get("actions") or []:
            action_slug = slugify(action)[:80] or f"tool-{len(out)+1}"
            action_title = action_slug.replace("-", " ").title()
            slug = pattern.format(action=action_slug)[:120]
            slug = slugify(slug.replace("/", "-"))[:120]
            name = name_pattern.format(Action=action_title, action=action_slug)
            description = desc_pattern.format(Action=action_title, action=action_slug.replace("-", " "))
            out.append(
                {
                    "slug": slug,
                    "category_slug": category_slug,
                    "recipe": recipe,
                    "name": {"en": name},
                    "description": {"en": description},
                    "ui_schema": dict(_DEFAULT_UI),
                    "pipeline": list(_DEFAULT_PIPELINE),
                    "seo": {
                        "title": {"en": f"{name} — Free Online Tool"},
                        "description": {"en": description},
                    },
                    "faq": [],
                    "howto": [
                        {"en": f"Open {name}"},
                        {"en": "Provide your input"},
                        {"en": "Run and download the result"},
                    ],
                    "capabilities": ["server"],
                }
            )
            if limit is not None and len(out) >= limit:
                return out
    return out


def queue_tool_expansion(
    *,
    category: str,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Create ToolSpec drafts from the expansion catalog.
    Never publishes — status is always draft.
    """
    limit = max(1, min(int(limit or 50), 500))
    candidates = iter_catalog_candidates(category, limit=limit)
    created = 0
    skipped = 0
    slugs: list[str] = []

    for item in candidates:
        slug = item["slug"]
        if ToolSpec.objects.filter(slug=slug).exists():
            skipped += 1
            continue
        ToolSpec.objects.create(
            slug=slug,
            category_slug=item["category_slug"],
            name=item["name"],
            description=item["description"],
            ui_schema=item["ui_schema"],
            pipeline=item["pipeline"],
            seo=item["seo"],
            faq=item["faq"],
            howto=item["howto"],
            capabilities=item["capabilities"],
            recipe=item["recipe"],
            status=ToolSpec.Status.DRAFT,
        )
        created += 1
        slugs.append(slug)

    catalog = load_expansion_catalog()
    return {
        "category": category,
        "created": created,
        "skipped": skipped,
        "limit": limit,
        "slugs": slugs,
        "catalog_capacity": catalog.get("capacity"),
        "status": ToolSpec.Status.DRAFT,
    }


def catalog_capacity_summary() -> dict[str, Any]:
    catalog = load_expansion_catalog()
    by_cat: dict[str, int] = {}
    total = 0
    for key in catalog.get("categories") or {}:
        n = len(iter_catalog_candidates(key))
        by_cat[key] = n
        total += n
    return {
        "declared_capacity": catalog.get("capacity"),
        "structural_slots": total,
        "by_category": by_cat,
    }
