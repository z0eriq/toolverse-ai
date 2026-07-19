"""Publish dynamic definitions into the unified Tool registry."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.tools_registry.discovery import CATEGORY_DEFAULTS
from apps.tools_registry.dynamic_models import DynamicToolDefinition
from apps.tools_registry.models import Category, Tool


@transaction.atomic
def publish_dynamic_tool(definition: DynamicToolDefinition) -> Tool:
    definition.mark_published()
    definition.save()

    meta = CATEGORY_DEFAULTS.get(definition.category_slug, {})
    category, _ = Category.objects.get_or_create(
        slug=definition.category_slug,
        defaults={
            "name": meta.get("name") or {"en": definition.category_slug.title()},
            "description": meta.get("description") or {"en": ""},
            "order": meta.get("order", 99),
        },
    )

    seo = definition.seo if isinstance(definition.seo, dict) else {}
    tool_id = f"dynamic:{definition.slug}"
    defaults = {
        "slug": definition.slug,
        "category": category,
        "name": definition.name,
        "description": definition.description,
        "version": definition.version,
        "premium": definition.premium,
        "adsense_slot": definition.adsense_slot or "sidebar",
        "seo_title": seo.get("title") or definition.name,
        "seo_description": seo.get("description") or definition.description,
        "seo_keywords": seo.get("keywords") or [],
        "schema_type": seo.get("schemaType") or "SoftwareApplication",
        "capabilities": definition.capabilities or ["server"],
        "icon": definition.icon,
        "is_active": True,
        "source": Tool.Source.DYNAMIC,
        "definition": definition,
        "faq": definition.faq or [],
        "howto_steps": definition.howto_steps or [],
    }
    tool, _ = Tool.objects.update_or_create(tool_id=tool_id, defaults=defaults)
    tool.rebuild_search_document()
    tool.save(update_fields=["search_document", "updated_at"])
    from apps.tools_registry.cache import invalidate_tool_caches

    invalidate_tool_caches(tool.slug)
    return tool


def sync_dynamic_tools() -> dict[str, int]:
    published = DynamicToolDefinition.objects.filter(status=DynamicToolDefinition.Status.PUBLISHED)
    count = 0
    for definition in published:
        publish_dynamic_tool(definition)
        count += 1
    # Soft-deactivate dynamic tools whose definition is no longer published
    active_ids = {f"dynamic:{d.slug}" for d in published}
    deactivated = (
        Tool.objects.filter(source=Tool.Source.DYNAMIC, is_active=True)
        .exclude(tool_id__in=active_ids)
        .update(is_active=False)
    )
    return {"published": count, "deactivated": deactivated}
