"""JWT decode API — header/payload only; never verifies or stores secrets."""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 100_000


class ToolThrottle(AnonRateThrottle):
    scope = "tool"


def _error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"success": False, "error": {"status_code": status_code, "message": message}},
        status=status_code,
    )


def _b64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _decode_json_segment(segment: str) -> Any:
    raw = _b64url_decode(segment)
    return json.loads(raw.decode("utf-8"))


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ToolThrottle])
def jwt_decoder_view(request) -> Response:
    """
    Body: { "token": "<jwt>" }

    Decodes header and payload only. Does not verify signatures.
    Optional secrets in the request body are ignored and never persisted.
    """
    payload = request.data if isinstance(request.data, dict) else {}
    token = payload.get("token", payload.get("jwt", payload.get("input", "")))
    if not isinstance(token, str):
        return _error("Field 'token' must be a string.")
    token = token.strip()
    if not token:
        return _error("token is required.")
    if len(token) > _MAX_CHARS:
        return _error(f"token exceeds maximum length of {_MAX_CHARS:,} characters.")

    # Explicitly discard any secret-like fields — never log or store them
    for key in ("secret", "key", "privateKey", "publicKey", "password"):
        payload.pop(key, None)

    parts = token.split(".")
    if len(parts) < 2:
        return _error("Invalid JWT: expected at least header and payload segments.")

    try:
        header = _decode_json_segment(parts[0])
        claims = _decode_json_segment(parts[1])
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return _error(f"Failed to decode JWT: {exc}")

    signature_present = len(parts) >= 3 and bool(parts[2])

    return Response(
        {
            "success": True,
            "data": {
                "header": header,
                "payload": claims,
                "signaturePresent": signature_present,
                "verified": False,
                "note": "Decoded without signature verification. Do not trust claims from untrusted tokens.",
            },
        }
    )
