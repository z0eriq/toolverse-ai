from __future__ import annotations

from django.db.models import Q

from apps.recommendations.models import ToolAffinity, ToolRelationship
from apps.tools_registry.models import Tool


def upsert_relationships_from_affinities(
    affinities: list[ToolAffinity] | None = None,
    *,
    reason: str = "affinity",
    replace_reason: bool = True,
) -> int:
    """Upsert directed ToolRelationship rows from undirected ToolAffinity pairs."""
    if affinities is None:
        rows = list(ToolAffinity.objects.all())
    else:
        rows = list(affinities)

    if replace_reason:
        ToolRelationship.objects.filter(reason=reason).delete()

    count = 0
    for row in rows:
        for source_id, target_id in (
            (row.tool_a_id, row.tool_b_id),
            (row.tool_b_id, row.tool_a_id),
        ):
            ToolRelationship.objects.update_or_create(
                source_tool_id=source_id,
                target_tool_id=target_id,
                defaults={
                    "relationship_score": row.score,
                    "reason": reason,
                },
            )
            count += 1
    return count


def get_related_tools(slug: str, limit: int = 6) -> list[Tool]:
    """
    Return related tools for ``slug``.

    Priority:
    1. Explicit ``Tool.related_slugs`` overrides
    2. ``ToolRelationship`` scores
    3. ``ToolAffinity`` scores
    4. Cold start: same category ordered by ``usage_count``
    """
    try:
        tool = Tool.objects.select_related("category").get(slug=slug, is_active=True)
    except Tool.DoesNotExist:
        return []

    overrides = tool.related_slugs if isinstance(tool.related_slugs, list) else []
    if overrides:
        by_slug = {
            t.slug: t
            for t in Tool.objects.filter(slug__in=overrides, is_active=True).select_related(
                "category"
            )
        }
        ordered = [by_slug[s] for s in overrides if s in by_slug and s != tool.slug]
        if ordered:
            return ordered[:limit]

    # Directed relationships (from affinity rebuild / manual curation)
    rel_ids: list[int] = []
    for row in (
        ToolRelationship.objects.filter(source_tool=tool)
        .select_related("target_tool")
        .order_by("-relationship_score")[: limit * 2]
    ):
        other = row.target_tool
        if other.is_active and other.pk != tool.pk and other.pk not in rel_ids:
            rel_ids.append(other.pk)
        if len(rel_ids) >= limit:
            break

    if rel_ids:
        tools_by_id = {
            t.pk: t
            for t in Tool.objects.filter(pk__in=rel_ids, is_active=True).select_related(
                "category"
            )
        }
        return [tools_by_id[i] for i in rel_ids if i in tools_by_id][:limit]

    affinity_ids: list[int] = []
    affinities = (
        ToolAffinity.objects.filter(Q(tool_a=tool) | Q(tool_b=tool))
        .select_related("tool_a", "tool_b")
        .order_by("-score")[: limit * 2]
    )
    for row in affinities:
        other = row.tool_b if row.tool_a_id == tool.pk else row.tool_a
        if other.is_active and other.pk != tool.pk and other.pk not in affinity_ids:
            affinity_ids.append(other.pk)
        if len(affinity_ids) >= limit:
            break

    if affinity_ids:
        tools_by_id = {
            t.pk: t
            for t in Tool.objects.filter(pk__in=affinity_ids, is_active=True).select_related(
                "category"
            )
        }
        return [tools_by_id[i] for i in affinity_ids if i in tools_by_id][:limit]

    return list(
        Tool.objects.filter(category=tool.category, is_active=True)
        .exclude(pk=tool.pk)
        .select_related("category")
        .order_by("-usage_count", "order", "slug")[:limit]
    )
