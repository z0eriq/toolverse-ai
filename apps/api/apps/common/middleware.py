from __future__ import annotations

import logging
import time
from typing import Callable

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone

logger = logging.getLogger("toolverse.request")

# Reasonable CSP for a JSON API (no HTML document serving expected).
API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        client_platform = str(request.META.get("HTTP_X_CLIENT_PLATFORM") or "")[:64]
        request.client_platform = client_platform  # type: ignore[attr-defined]
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000
        if client_platform:
            logger.info(
                "method=%s path=%s status=%s duration_ms=%.2f client_platform=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                client_platform,
            )
        else:
            logger.info(
                "method=%s path=%s status=%s duration_ms=%.2f",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )
        return response


class SecurityHeadersMiddleware:
    """Add defense-in-depth security headers for API responses."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", API_CSP)
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        return response


class BlockedIPMiddleware:
    """Soft IP blocklist check — returns 403 JSON when the client IP is blocked."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ip = self._client_ip(request)
        if ip and self._is_blocked(ip):
            return JsonResponse(
                {
                    "success": False,
                    "error": {
                        "status_code": 403,
                        "message": "Forbidden",
                    },
                },
                status=403,
            )
        return self.get_response(request)

    @staticmethod
    def _client_ip(request: HttpRequest) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip() or None
        return request.META.get("REMOTE_ADDR") or None

    @staticmethod
    def _is_blocked(ip: str) -> bool:
        try:
            from apps.common.models import BlockedIP

            now = timezone.now()
            return (
                BlockedIP.objects.filter(ip=ip, is_active=True)
                .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
                .exists()
            )
        except Exception:  # noqa: BLE001
            # Soft: never block traffic if DB lookup fails.
            return False
