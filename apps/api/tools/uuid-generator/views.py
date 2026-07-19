"""UUID generation API."""

from __future__ import annotations

import uuid

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_COUNT = 100


class ToolThrottle(AnonRateThrottle):
    scope = "tool"


def _error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"success": False, "error": {"status_code": status_code, "message": message}},
        status=status_code,
    )


def _generate_one(version: int, namespace: str | None, name: str | None) -> str:
    if version == 1:
        return str(uuid.uuid1())
    if version == 4:
        return str(uuid.uuid4())
    if version == 5:
        ns_map = {
            "dns": uuid.NAMESPACE_DNS,
            "url": uuid.NAMESPACE_URL,
            "oid": uuid.NAMESPACE_OID,
            "x500": uuid.NAMESPACE_X500,
        }
        ns_key = (namespace or "dns").lower()
        if ns_key not in ns_map:
            raise ValueError("namespace must be one of: dns, url, oid, x500.")
        if not name:
            raise ValueError("name is required for UUID v5.")
        return str(uuid.uuid5(ns_map[ns_key], name))
    raise ValueError("version must be 1, 4, or 5.")


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@throttle_classes([ToolThrottle])
def uuid_generator_view(request) -> Response:
    """
    GET/POST query or body:
      version: 1 | 4 | 5 (default 4)
      count: 1..100 (default 1)
      namespace: dns | url | oid | x500 (v5)
      name: string (v5)
      uppercase?: bool
    """
    source = request.query_params if request.method == "GET" else (
        request.data if isinstance(request.data, dict) else {}
    )

    try:
        version = int(source.get("version", 4))
    except (TypeError, ValueError):
        return _error("version must be an integer (1, 4, or 5).")

    try:
        count = int(source.get("count", 1))
    except (TypeError, ValueError):
        return _error("count must be an integer.")
    if count < 1 or count > _MAX_COUNT:
        return _error(f"count must be between 1 and {_MAX_COUNT}.")

    namespace = source.get("namespace")
    name = source.get("name")
    if namespace is not None and not isinstance(namespace, str):
        return _error("namespace must be a string.")
    if name is not None and not isinstance(name, str):
        return _error("name must be a string.")

    uppercase = str(source.get("uppercase", "false")).lower() in {"1", "true", "yes"}

    try:
        values = [_generate_one(version, namespace, name) for _ in range(count)]
    except ValueError as exc:
        return _error(str(exc))

    if uppercase:
        values = [v.upper() for v in values]

    return Response(
        {
            "success": True,
            "data": {
                "version": version,
                "count": count,
                "uuids": values,
                "uuid": values[0],
            },
        }
    )
