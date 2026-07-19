from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from itertools import combinations

from celery import shared_task
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.favorites.models import Favorite
from apps.history.models import ToolHistory
from apps.recommendations.models import ToolAffinity


def _pair_key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


@shared_task(name="apps.recommendations.tasks.rebuild_tool_affinities")
def rebuild_tool_affinities(history_days: int = 90) -> dict:
    """
    Rebuild ToolAffinity from:
    - ToolHistory co-occurrence (same user, same calendar day ≈ 24h session)
    - Favorite pairs for the same user
    """
    scores: dict[tuple[int, int], float] = defaultdict(float)
    cutoff = timezone.now() - timedelta(days=history_days)

    # History: group by user + day, then count pairwise co-occurrence
    history_rows = (
        ToolHistory.objects.filter(created_at__gte=cutoff)
        .annotate(day=TruncDate("created_at"))
        .values("user_id", "day", "tool_id")
        .annotate(n=Count("id"))
    )
    by_session: dict[tuple[int, object], set[int]] = defaultdict(set)
    for row in history_rows:
        by_session[(row["user_id"], row["day"])].add(row["tool_id"])

    for tool_ids in by_session.values():
        if len(tool_ids) < 2:
            continue
        for a, b in combinations(sorted(tool_ids), 2):
            scores[_pair_key(a, b)] += 1.0

    # Favorites: tools favorited by the same user
    fav_by_user: dict[int, set[int]] = defaultdict(set)
    for user_id, tool_id in Favorite.objects.values_list("user_id", "tool_id"):
        fav_by_user[user_id].add(tool_id)

    for tool_ids in fav_by_user.values():
        if len(tool_ids) < 2:
            continue
        for a, b in combinations(sorted(tool_ids), 2):
            # Favorites are a slightly stronger signal
            scores[_pair_key(a, b)] += 1.5

    if not scores:
        deleted, _ = ToolAffinity.objects.all().delete()
        from apps.recommendations.models import ToolRelationship

        rel_deleted, _ = ToolRelationship.objects.filter(reason="affinity_rebuild").delete()
        return {"pairs": 0, "deleted": deleted, "relationships_deleted": rel_deleted}

    max_score = max(scores.values()) or 1.0

    with transaction.atomic():
        ToolAffinity.objects.all().delete()
        created = ToolAffinity.objects.bulk_create(
            [
                ToolAffinity(
                    tool_a_id=a,
                    tool_b_id=b,
                    score=round(raw / max_score, 6),
                )
                for (a, b), raw in scores.items()
            ],
            batch_size=500,
        )

    from apps.recommendations.services import upsert_relationships_from_affinities

    relationships = upsert_relationships_from_affinities(created, reason="affinity_rebuild")

    return {
        "pairs": len(scores),
        "max_raw": max_score,
        "relationships": relationships,
    }
