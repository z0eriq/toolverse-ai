"""Safe HTTP response caching helpers (tolerate Redis/backend outages)."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from django.views.decorators.cache import cache_page


def cache_page_safe(
    timeout: int,
    *,
    key_prefix: str = "",
    cache: str = "default",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Like Django's ``cache_page``, but falls through to the view if the
    cache backend raises (e.g. Redis unreachable).
    """

    def decorator(view_func: Callable[..., Any]) -> Callable[..., Any]:
        cached_view = cache_page(timeout, key_prefix=key_prefix, cache=cache)(view_func)

        @wraps(view_func)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return cached_view(*args, **kwargs)
            except Exception:  # noqa: BLE001
                return view_func(*args, **kwargs)

        return _wrapped

    return decorator
