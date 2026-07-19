"""Cryptographic hash generation API (MD5 / SHA-256 / SHA-512)."""

from __future__ import annotations

import hashlib

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 1_000_000
_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


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
def hash_generator_view(request) -> Response:
    """
    Body: {
      "input": "<string>",
      "algorithm": "md5" | "sha256" | "sha512" | "all",
      "encoding"?: "utf-8" | "hex" | "base64"
    }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    raw = payload.get("input", payload.get("text", ""))
    if not isinstance(raw, str):
        return _error("Field 'input' must be a string.")
    if len(raw) > _MAX_CHARS:
        return _error(f"Input exceeds maximum length of {_MAX_CHARS:,} characters.")

    algorithm = str(payload.get("algorithm", "all")).lower().strip()
    if algorithm not in {*_ALGORITHMS.keys(), "all"}:
        return _error("algorithm must be one of: md5, sha256, sha512, all.")

    encoding = str(payload.get("encoding", "utf-8")).lower().strip()
    try:
        if encoding == "utf-8":
            data = raw.encode("utf-8")
        elif encoding == "hex":
            data = bytes.fromhex(raw.replace(" ", "").replace("0x", ""))
        elif encoding == "base64":
            import base64

            padded = raw.strip()
            missing = len(padded) % 4
            if missing:
                padded += "=" * (4 - missing)
            data = base64.b64decode(padded)
        else:
            return _error("encoding must be one of: utf-8, hex, base64.")
    except (ValueError, TypeError) as exc:
        return _error(f"Failed to decode input with encoding '{encoding}': {exc}")

    selected = list(_ALGORITHMS.keys()) if algorithm == "all" else [algorithm]
    hashes = {name: _ALGORITHMS[name](data).hexdigest() for name in selected}

    return Response(
        {
            "success": True,
            "data": {
                "algorithm": algorithm,
                "encoding": encoding,
                "byteLength": len(data),
                "hashes": hashes,
                "hash": hashes[selected[0]] if len(selected) == 1 else None,
            },
        }
    )
