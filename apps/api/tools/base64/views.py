"""Base64 encode / decode API."""

from __future__ import annotations

import base64
import binascii

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
def base64_view(request) -> Response:
    """
    Body: { "input": "<string>", "action": "encode" | "decode", "urlSafe"?: bool }
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

    url_safe = bool(payload.get("urlSafe", payload.get("url_safe", False)))

    try:
        if action == "encode":
            data = raw.encode("utf-8")
            encoded = (
                base64.urlsafe_b64encode(data) if url_safe else base64.b64encode(data)
            )
            output = encoded.decode("ascii")
        else:
            # Tolerate missing padding
            padded = raw.strip()
            missing = len(padded) % 4
            if missing:
                padded += "=" * (4 - missing)
            decoder = base64.urlsafe_b64decode if url_safe else base64.b64decode
            decoded = decoder(padded, validate=False)
            try:
                output = decoded.decode("utf-8")
            except UnicodeDecodeError:
                output = decoded.hex()
                return Response(
                    {
                        "success": True,
                        "data": {
                            "action": action,
                            "urlSafe": url_safe,
                            "output": output,
                            "encoding": "hex",
                            "note": "Decoded bytes are not valid UTF-8; returned as hex.",
                        },
                    }
                )
    except (binascii.Error, ValueError) as exc:
        return _error(f"Invalid Base64 input: {exc}")

    return Response(
        {
            "success": True,
            "data": {
                "action": action,
                "urlSafe": url_safe,
                "output": output,
                "encoding": "utf-8",
            },
        }
    )
