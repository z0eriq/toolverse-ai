"""URL percent-encode / decode API."""

from __future__ import annotations

from urllib.parse import quote, quote_plus, unquote, unquote_plus

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 500_000


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
def url_encoder_view(request) -> Response:
    """
    Body: {
      "input": "<string>",
      "action": "encode" | "decode",
      "mode"?: "component" | "form"   # component=quote, form=quote_plus
      "safe"?: string                  # extra safe chars for encode (component mode)
    }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    raw = payload.get("input", payload.get("text", ""))
    if not isinstance(raw, str):
        return _error("Field 'input' must be a string.")
    if len(raw) > _MAX_CHARS:
        return _error(f"Input exceeds maximum length of {_MAX_CHARS:,} characters.")

    action = str(payload.get("action", "encode")).lower().strip()
    if action not in {"encode", "decode"}:
        return _error("action must be one of: encode, decode.")

    mode = str(payload.get("mode", "component")).lower().strip()
    if mode not in {"component", "form"}:
        return _error("mode must be one of: component, form.")

    safe = payload.get("safe", "")
    if safe is not None and not isinstance(safe, str):
        return _error("safe must be a string.")
    safe = safe or ""

    if action == "encode":
        output = quote_plus(raw, safe=safe) if mode == "form" else quote(raw, safe=safe)
    else:
        output = unquote_plus(raw) if mode == "form" else unquote(raw)

    return Response(
        {
            "success": True,
            "data": {
                "action": action,
                "mode": mode,
                "output": output,
            },
        }
    )
