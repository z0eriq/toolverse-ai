from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from django.conf import settings
from django.db.models import Avg, Sum
from django.utils import timezone

from apps.search_console.models import GSCMetricSnapshot, GSCProperty, IndexedUrl


logger = logging.getLogger("toolverse.search_console")


def _credentials_available() -> bool:
    raw = getattr(settings, "GSC_CREDENTIALS_JSON", "") or ""
    if raw.strip():
        return True
    path = getattr(settings, "GSC_CREDENTIALS_FILE", "") or ""
    return bool(path and Path(path).exists())


def _load_credentials() -> dict[str, Any] | None:
    raw = getattr(settings, "GSC_CREDENTIALS_JSON", "") or ""
    if raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("GSC_CREDENTIALS_JSON is not valid JSON")
            return None
    path = getattr(settings, "GSC_CREDENTIALS_FILE", "") or ""
    if path and Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to read GSC credentials file: %s", exc)
            return None
    return None


def sync_search_analytics(
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    """
    Sync Search Console analytics into GSCMetricSnapshot.
    Returns early with skipped when credentials are not configured.
    """
    if not _credentials_available():
        return {"synced": 0, "skipped": "no_credentials"}

    creds = _load_credentials()
    if not creds:
        return {"synced": 0, "skipped": "invalid_credentials"}

    end = end or timezone.now().date()
    start = start or (end - timedelta(days=3))

    # Live Google API sync is optional; without google-api client we record a
    # zero-row successful sync so admin UIs stay healthy.
    properties = list(GSCProperty.objects.filter(is_active=True))
    if not properties:
        prop, _ = GSCProperty.objects.get_or_create(
            site_url=getattr(settings, "GSC_SITE_URL", "https://toolverse.ai/") or "https://toolverse.ai/",
            defaults={"credentials_ref": "GSC_CREDENTIALS_JSON", "is_active": True},
        )
        properties = [prop]

    synced = 0
    try:
        # Prefer googleapiclient when installed; otherwise no-op success.
        from google.oauth2 import service_account  # type: ignore
        from googleapiclient.discovery import build  # type: ignore

        credentials = service_account.Credentials.from_service_account_info(
            creds,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        for prop in properties:
            body = {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["page", "query", "country", "device"],
                "rowLimit": 1000,
            }
            response = (
                service.searchanalytics()
                .query(siteUrl=prop.site_url, body=body)
                .execute()
            )
            for row in response.get("rows") or []:
                keys = row.get("keys") or ["", "", "", ""]
                page = keys[0] if len(keys) > 0 else ""
                query = keys[1] if len(keys) > 1 else ""
                country = keys[2] if len(keys) > 2 else ""
                device = keys[3] if len(keys) > 3 else ""
                GSCMetricSnapshot.objects.create(
                    property=prop,
                    date=end,
                    page=page[:1024],
                    query=query[:512],
                    country=country[:8],
                    device=device[:32],
                    clicks=int(row.get("clicks") or 0),
                    impressions=int(row.get("impressions") or 0),
                    ctr=float(row.get("ctr") or 0),
                    position=float(row.get("position") or 0),
                )
                synced += 1
    except ImportError:
        logger.info("google-api-python-client not installed; GSC sync no-op with credentials present")
        return {
            "synced": 0,
            "skipped": "client_missing",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "properties": len(properties),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("GSC sync failed")
        return {"synced": synced, "error": str(exc)[:2000]}

    keywords_result: dict[str, Any] | None = None
    try:
        from apps.keywords.services import upsert_keywords_from_gsc

        keywords_result = upsert_keywords_from_gsc()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Keyword upsert after GSC sync failed: %s", exc)

    indexed_result: dict[str, Any] | None = None
    try:
        indexed_result = upsert_indexed_urls_from_gsc()
    except Exception as exc:  # noqa: BLE001
        logger.warning("IndexedUrl upsert after GSC sync failed: %s", exc)

    return {
        "synced": synced,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "properties": len(properties),
        "keywords": keywords_result,
        "indexed_urls": indexed_result,
    }


def _normalize_url_path(page: str) -> str:
    """Extract a stable path key from a full URL or path string."""
    raw = (page or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlparse(raw)
        path = parsed.path or raw
    except Exception:  # noqa: BLE001
        path = raw
    if not path.startswith("/"):
        path = "/" + path
    # Drop trailing slash except root
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path[:1024]


def upsert_indexed_urls_from_gsc() -> dict[str, Any]:
    """
    Aggregate GSCMetricSnapshot by page and upsert IndexedUrl rows.
    Pages with impressions are marked indexed; ranking_delta vs prior position.
    """
    rows = (
        GSCMetricSnapshot.objects.exclude(page="")
        .values("page")
        .annotate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_position=Avg("position"),
        )
        .order_by("-impressions")
    )

    now = timezone.now()
    created = updated = 0
    for row in rows:
        url_path = _normalize_url_path(str(row.get("page") or ""))
        if not url_path:
            continue
        impressions = int(row.get("impressions") or 0)
        clicks = int(row.get("clicks") or 0)
        position = row.get("avg_position")
        position_f = float(position) if position is not None else None

        existing = IndexedUrl.objects.filter(url_path=url_path).first()
        ranking_delta = None
        if existing and existing.position is not None and position_f is not None:
            ranking_delta = round(existing.position - position_f, 4)

        status = IndexedUrl.Status.INDEXED if impressions > 0 else IndexedUrl.Status.CRAWLED
        defaults = {
            "impressions": impressions,
            "clicks": clicks,
            "position": position_f,
            "ranking_delta": ranking_delta if ranking_delta is not None else (existing.ranking_delta if existing else None),
            "status": status,
            "last_crawled_at": now,
        }
        obj, was_created = IndexedUrl.objects.update_or_create(
            url_path=url_path,
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1
            _ = obj  # silence unused

    return {"created": created, "updated": updated, "total": created + updated}


def overview_aggregates(days: int = 28) -> dict[str, Any]:
    since = timezone.now().date() - timedelta(days=days)
    qs = GSCMetricSnapshot.objects.filter(date__gte=since)
    totals = qs.aggregate(
        clicks=Sum("clicks"),
        impressions=Sum("impressions"),
        avg_ctr=Avg("ctr"),
        avg_position=Avg("position"),
    )
    return {
        "days": days,
        "clicks": totals.get("clicks") or 0,
        "impressions": totals.get("impressions") or 0,
        "avg_ctr": totals.get("avg_ctr") or 0,
        "avg_position": totals.get("avg_position") or 0,
        "row_count": qs.count(),
    }


def top_queries(days: int = 28, limit: int = 50) -> list[dict[str, Any]]:
    since = timezone.now().date() - timedelta(days=days)
    rows = (
        GSCMetricSnapshot.objects.filter(date__gte=since)
        .exclude(query="")
        .values("query")
        .annotate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_ctr=Avg("ctr"),
            avg_position=Avg("position"),
        )
        .order_by("-clicks")[:limit]
    )
    return list(rows)


def top_pages(days: int = 28, limit: int = 50) -> list[dict[str, Any]]:
    since = timezone.now().date() - timedelta(days=days)
    rows = (
        GSCMetricSnapshot.objects.filter(date__gte=since)
        .exclude(page="")
        .values("page")
        .annotate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_ctr=Avg("ctr"),
            avg_position=Avg("position"),
        )
        .order_by("-clicks")[:limit]
    )
    return list(rows)
