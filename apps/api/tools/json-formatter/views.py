"""JSON validate / format / minify API."""

from __future__ import annotations

import json
from typing import Any

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 1_000_000


class ToolThrottle(AnonRateThrottle):
    scope = "tool"


def _error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"success": False, "error": {"status_code": status_code, "message": message}},
        status=status_code,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ToolThrottle])
def json_formatter_view(request) -> Response:
    """
    Body: { "json": "<string>", "action": "validate" | "format" | "minify", "indent"?: number }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    raw = payload.get("json", payload.get("input", ""))
    if not isinstance(raw, str):
        return _error("Field 'json' must be a string.")
    if len(raw) > _MAX_CHARS:
        return _error(f"Input exceeds maximum length of {_MAX_CHARS:,} characters.")

    action = str(payload.get("action", "format")).lower().strip()
    if action not in {"validate", "format", "minify"}:
        return _error("action must be one of: validate, format, minify.")

    indent_raw = payload.get("indent", 2)
    try:
        indent = int(indent_raw)
    except (TypeError, ValueError):
        return _error("indent must be an integer between 0 and 8.")
    if indent < 0 or indent > 8:
        return _error("indent must be an integer between 0 and 8.")

    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        return Response(
            {
                "success": True,
                "data": {
                    "valid": False,
                    "action": action,
                    "error": {
                        "message": exc.msg,
                        "line": exc.lineno,
                        "column": exc.colno,
                        "pos": exc.pos,
                    },
                },
            }
        )

    result: dict[str, Any] = {"valid": True, "action": action}
    if action == "validate":
        result["type"] = type(parsed).__name__
    elif action == "format":
        result["output"] = json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=False)
    else:
        result["output"] = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)

    return Response({"success": True, "data": result})
