from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions, serializers
from rest_framework.views import APIView

from apps.analytics.models import AnalyticsDailyRollup, AnalyticsEvent
from apps.common.exceptions import success_response


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "is_admin", False) or user.is_staff)
        )


def _resolve_country(request, provided: str = "") -> str:
    if provided:
        return provided[:2].upper()
    cf = request.META.get("HTTP_CF_IPCOUNTRY") or request.META.get("HTTP_X_GEO_COUNTRY") or ""
    cf = cf.strip().upper()
    if cf in {"XX", "T1"}:
        return ""
    return cf[:2] if cf else ""


def _hash_user_agent(request, provided: str = "") -> str:
    if provided:
        return provided[:64]
    ua = request.META.get("HTTP_USER_AGENT", "")
    if not ua:
        return ""
    return hashlib.sha256(ua.encode("utf-8")).hexdigest()


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = (
            "name",
            "session_id",
            "path",
            "properties",
            "tool_id",
            "country",
            "referrer",
            "user_agent_hash",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "campaign_key",
        )
        extra_kwargs = {
            "tool_id": {"required": False, "allow_blank": True},
            "country": {"required": False, "allow_blank": True},
            "referrer": {"required": False, "allow_blank": True},
            "user_agent_hash": {"required": False, "allow_blank": True},
            "utm_source": {"required": False, "allow_blank": True},
            "utm_medium": {"required": False, "allow_blank": True},
            "utm_campaign": {"required": False, "allow_blank": True},
            "campaign_key": {"required": False, "allow_blank": True},
        }


def _copy_utm_from_properties(data: dict) -> dict:
    """Fill top-level UTM / campaign_key from properties when missing."""
    props = data.get("properties") or {}
    if not isinstance(props, dict):
        return data
    for field in ("utm_source", "utm_medium", "utm_campaign", "campaign_key"):
        if not data.get(field):
            value = props.get(field) or ""
            if value:
                data[field] = str(value)[:128]
    return data


class TrackEventView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = AnalyticsEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data = _copy_utm_from_properties(data)
        data["country"] = _resolve_country(request, data.get("country", ""))
        data["user_agent_hash"] = _hash_user_agent(request, data.get("user_agent_hash", ""))
        event = AnalyticsEvent.objects.create(
            user=request.user if request.user.is_authenticated else None,
            **data,
        )
        return success_response({"id": event.id})


class FunnelView(APIView):
    """Admin conversion funnel (impression → revenue)."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        from apps.analytics.funnels import build_conversion_funnel

        days = request.query_params.get("days") or 30
        try:
            days_int = int(days)
        except (TypeError, ValueError):
            days_int = 30
        return success_response(build_conversion_funnel(days=days_int))


class DashboardView(APIView):
    """Admin-only analytics dashboard (last 30 days)."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        now = timezone.now()
        since = now - timedelta(days=30)
        events = AnalyticsEvent.objects.filter(created_at__gte=since)

        # Usage series by day
        series_qs = (
            events.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        usage_series = [
            {"date": row["day"].isoformat(), "count": row["count"]} for row in series_qs
        ]

        # CTR-style funnel: impressions / clicks / uses
        name_counts = dict(
            events.values("name").annotate(c=Count("id")).values_list("name", "c")
        )

        def _count(*aliases: str) -> int:
            return sum(name_counts.get(a, 0) for a in aliases)

        impressions = _count("impression", "tool_impression", "view")
        clicks = _count("click", "tool_click")
        uses = _count("use", "tool_use", "tool_run", "run")
        ctr = {
            "impressions": impressions,
            "clicks": clicks,
            "uses": uses,
            "click_through_rate": round(clicks / impressions, 4) if impressions else 0.0,
            "use_rate": round(uses / clicks, 4) if clicks else 0.0,
        }

        retention = self._retention(since)
        geo = list(
            events.exclude(country="")
            .values("country")
            .annotate(count=Count("id"))
            .order_by("-count")[:15]
        )
        top_tools = list(
            events.exclude(tool_id="")
            .values("tool_id")
            .annotate(count=Count("id"))
            .order_by("-count")[:15]
        )

        # Prefer rollups when available for series enrichment
        rollup_total = (
            AnalyticsDailyRollup.objects.filter(date__gte=since.date()).aggregate(
                total=Sum("count")
            )["total"]
            or 0
        )

        return success_response(
            {
                "window_days": 30,
                "usage_series": usage_series,
                "ctr": ctr,
                "retention": retention,
                "geo": geo,
                "top_tools": top_tools,
                "rollup_event_total": rollup_total,
            }
        )

    @staticmethod
    def _retention(since) -> dict:
        """
        Approximate D1 / D7 / D30 retention using session_id (fallback: user_id).
        Cohort = actors with first activity in the window; Dn = returned n days later.
        """
        rows = (
            AnalyticsEvent.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("session_id", "user_id", "day")
        )
        first_day: dict[str, object] = {}
        active_days: dict[str, set] = defaultdict(set)

        for row in rows:
            actor = row["session_id"] or (f"u:{row['user_id']}" if row["user_id"] else "")
            if not actor:
                continue
            day = row["day"]
            active_days[actor].add(day)
            if actor not in first_day or day < first_day[actor]:
                first_day[actor] = day

        cohort = len(first_day)
        if cohort == 0:
            return {"cohort": 0, "d1": 0.0, "d7": 0.0, "d30": 0.0}

        def rate(offset: int) -> float:
            returned = 0
            for actor, start in first_day.items():
                target = start + timedelta(days=offset)
                if target in active_days[actor]:
                    returned += 1
            return round(returned / cohort, 4)

        return {
                "cohort": cohort,
                "d1": rate(1),
                "d7": rate(7),
                "d30": rate(30),
            }


class GrowthDashboardView(APIView):
    """Admin growth metrics (last 30 days). Extends analytics without changing DashboardView."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        now = timezone.now()
        since = now - timedelta(days=30)
        events = AnalyticsEvent.objects.filter(created_at__gte=since)

        name_counts = dict(
            events.values("name").annotate(c=Count("id")).values_list("name", "c")
        )

        def _count(*aliases: str) -> int:
            return sum(name_counts.get(a, 0) for a in aliases)

        search_impressions = _count("search_impression", "search_impressions")
        tool_views = _count("tool_view", "view", "impression", "tool_impression")
        tool_usage = _count("use", "tool_use", "tool_run", "run")
        conversion_rate = round(tool_usage / tool_views, 4) if tool_views else 0.0

        returning_users = self._returning_users_estimate(since)
        languages = self._languages(events)
        traffic_sources = self._traffic_sources(events)

        return success_response(
            {
                "window_days": 30,
                "search_impressions": search_impressions,
                "tool_views": tool_views,
                "tool_usage": tool_usage,
                "conversion_rate": conversion_rate,
                "returning_users": returning_users,
                "languages": languages,
                "traffic_sources": traffic_sources,
            }
        )

    @staticmethod
    def _returning_users_estimate(since) -> dict:
        """Actors with activity on 2+ distinct days in the window."""
        rows = (
            AnalyticsEvent.objects.filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("session_id", "user_id", "day")
        )
        active_days: dict[str, set] = defaultdict(set)
        for row in rows:
            actor = row["session_id"] or (f"u:{row['user_id']}" if row["user_id"] else "")
            if not actor:
                continue
            active_days[actor].add(row["day"])

        total = len(active_days)
        returning = sum(1 for days in active_days.values() if len(days) >= 2)
        return {
            "total_actors": total,
            "returning_actors": returning,
            "returning_rate": round(returning / total, 4) if total else 0.0,
        }

    @staticmethod
    def _languages(events) -> list[dict]:
        counts: dict[str, int] = defaultdict(int)
        for props in events.exclude(properties={}).values_list("properties", flat=True):
            if not isinstance(props, dict):
                continue
            lang = (
                props.get("locale")
                or props.get("language")
                or props.get("lang")
                or ""
            )
            lang = str(lang).strip().lower()[:10]
            if lang:
                counts[lang] += 1
        return [
            {"locale": k, "count": v}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])[:20]
        ]

    @staticmethod
    def _traffic_sources(events) -> list[dict]:
        from urllib.parse import urlparse

        counts: dict[str, int] = defaultdict(int)
        for ref in events.exclude(referrer="").values_list("referrer", flat=True):
            try:
                host = urlparse(ref).netloc.lower() or "direct"
            except Exception:  # noqa: BLE001
                host = "unknown"
            if host.startswith("www."):
                host = host[4:]
            counts[host or "direct"] += 1
        return [
            {"host": k, "count": v}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])[:20]
        ]


class CommandCenterView(APIView):
    """Admin executive command center KPIs."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        from apps.analytics.command_center import build_command_center

        days = request.query_params.get("days") or 30
        try:
            days_int = int(days)
        except (TypeError, ValueError):
            days_int = 30
        return success_response(build_command_center(days=days_int))
