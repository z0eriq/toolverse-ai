"""Audit logging helpers."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from apps.common.models import AuditLog


def _client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def _user_agent(request: HttpRequest | None) -> str:
    if request is None:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:512]


def log_audit(
    request: HttpRequest | None,
    action: str,
    *,
    resource_type: str = "",
    resource_id: str | int | None = "",
    meta: dict[str, Any] | None = None,
    actor=None,
) -> AuditLog:
    """
    Persist an audit log row. Never raises — audit failures must not break
    the primary request path.
    """
    user = actor
    if user is None and request is not None:
        user = getattr(request, "user", None)
        if user is not None and not getattr(user, "is_authenticated", False):
            user = None

    rid = "" if resource_id is None else str(resource_id)

    try:
        return AuditLog.objects.create(
            actor=user,
            action=action,
            resource_type=resource_type or "",
            resource_id=rid,
            ip=_client_ip(request),
            user_agent=_user_agent(request),
            meta=meta or {},
        )
    except Exception:  # noqa: BLE001
        # Soft-fail: audit must not take down API mutations.
        return AuditLog(
            actor=user,
            action=action,
            resource_type=resource_type or "",
            resource_id=rid,
            ip=_client_ip(request),
            user_agent=_user_agent(request),
            meta=meta or {},
        )
