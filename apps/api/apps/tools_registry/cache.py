"""Redis-backed tool list/detail cache helpers."""

from __future__ import annotations

from django.core.cache import cache

TOOLS_LIST_KEY = "tools:list:v1"
TOOL_DETAIL_KEY = "tools:detail:{slug}:v1"
TOOL_RELATED_KEY = "tools:related:{slug}:v1"


def invalidate_tool_caches(slug: str | None = None) -> None:
    cache.delete(TOOLS_LIST_KEY)
    if slug:
        cache.delete(TOOL_DETAIL_KEY.format(slug=slug))
        cache.delete(TOOL_RELATED_KEY.format(slug=slug))


def cache_get(key: str):
    try:
        return cache.get(key)
    except Exception:  # noqa: BLE001
        return None


def cache_set(key: str, value, timeout: int = 300) -> None:
    try:
        cache.set(key, value, timeout)
    except Exception:  # noqa: BLE001
        pass
