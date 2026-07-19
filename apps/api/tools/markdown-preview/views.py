"""Markdown → sanitized HTML preview API."""

from __future__ import annotations

import bleach
import markdown
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 200_000

_ALLOWED_TAGS = [
    "a", "abbr", "b", "blockquote", "br", "code", "dd", "del", "div", "dl", "dt",
    "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "ins", "kbd",
    "li", "ol", "p", "pre", "q", "s", "samp", "span", "strong", "sub", "sup",
    "table", "tbody", "td", "th", "thead", "tr", "ul",
]

_ALLOWED_ATTRIBUTES = {
    "*": ["class", "id", "title"],
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "td": ["colspan", "rowspan", "align"],
    "th": ["colspan", "rowspan", "align"],
}

_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


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
def markdown_preview_view(request) -> Response:
    """
    Body: { "markdown": "<string>", "extensions"?: string[] }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    raw = payload.get("markdown", payload.get("input", payload.get("text", "")))
    if not isinstance(raw, str):
        return _error("Field 'markdown' must be a string.")
    if len(raw) > _MAX_CHARS:
        return _error(f"Input exceeds maximum length of {_MAX_CHARS:,} characters.")

    requested = payload.get("extensions")
    allowed_ext = {"extra", "sane_lists", "smarty", "tables", "fenced_code", "nl2br", "toc"}
    if requested is None:
        extensions = ["extra", "sane_lists", "smarty", "tables", "fenced_code"]
    elif isinstance(requested, list) and all(isinstance(x, str) for x in requested):
        extensions = [x for x in requested if x in allowed_ext]
    else:
        return _error("extensions must be an array of extension names.")

    html = markdown.markdown(
        raw,
        extensions=extensions,
        output_format="html",
    )
    clean = bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )
    # Force safe link behavior
    clean = bleach.linkify(clean, parse_email=True)

    return Response(
        {
            "success": True,
            "data": {
                "html": clean,
                "extensions": extensions,
                "inputLength": len(raw),
            },
        }
    )
