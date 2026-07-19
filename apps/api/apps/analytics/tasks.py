from datetime import timedelta

from celery import shared_task
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.analytics.models import AnalyticsDailyRollup, AnalyticsEvent


@shared_task(name="apps.analytics.tasks.rollup_analytics_daily")
def rollup_analytics_daily(days: int = 2) -> dict:
    """
    Aggregate AnalyticsEvent into AnalyticsDailyRollup for recent days.

    Idempotent upsert by (date, tool_id, event_name, country).
    """
    since = timezone.now() - timedelta(days=days)
    grouped = (
        AnalyticsEvent.objects.filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day", "tool_id", "name", "country")
        .annotate(count=Count("id"))
    )

    upserted = 0
    for row in grouped:
        AnalyticsDailyRollup.objects.update_or_create(
            date=row["day"],
            tool_id=row["tool_id"] or "",
            event_name=row["name"],
            country=row["country"] or "",
            defaults={"count": row["count"]},
        )
        upserted += 1

    return {"upserted": upserted, "days": days}
