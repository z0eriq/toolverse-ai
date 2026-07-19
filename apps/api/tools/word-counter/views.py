"""Word / character / reading-time counter API."""

from __future__ import annotations

import math
import re

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_MAX_CHARS = 1_000_000
_WORD_RE = re.compile(r"\b[\w']+\b", re.UNICODE)
_SENTENCE_RE = re.compile(r"[^.!?…]+[.!?…]+|[^.!?…]+$", re.UNICODE)
_PARAGRAPH_RE = re.compile(r"\n\s*\n+")


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
def word_counter_view(request) -> Response:
    """
    Body: { "text": "<string>", "wordsPerMinute"?: number }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    text = payload.get("text", payload.get("input", ""))
    if not isinstance(text, str):
        return _error("Field 'text' must be a string.")
    if len(text) > _MAX_CHARS:
        return _error(f"Input exceeds maximum length of {_MAX_CHARS:,} characters.")

    try:
        wpm = float(payload.get("wordsPerMinute", payload.get("words_per_minute", 200)))
    except (TypeError, ValueError):
        return _error("wordsPerMinute must be a number.")
    if wpm <= 0 or wpm > 2000:
        return _error("wordsPerMinute must be between 1 and 2000.")

    words = _WORD_RE.findall(text)
    word_count = len(words)
    char_count = len(text)
    char_no_spaces = len(re.sub(r"\s+", "", text))
    lines = text.splitlines() if text else []
    line_count = len(lines) if text else 0
    paragraphs = [p for p in _PARAGRAPH_RE.split(text.strip()) if p.strip()] if text.strip() else []
    sentences = [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()] if text.strip() else []

    minutes = word_count / wpm if word_count else 0.0
    reading_minutes = math.ceil(minutes) if minutes > 0 else 0
    reading_seconds = int(round(minutes * 60))

    return Response(
        {
            "success": True,
            "data": {
                "words": word_count,
                "characters": char_count,
                "charactersNoSpaces": char_no_spaces,
                "sentences": len(sentences),
                "paragraphs": len(paragraphs),
                "lines": line_count,
                "wordsPerMinute": wpm,
                "readingTime": {
                    "minutes": reading_minutes,
                    "seconds": reading_seconds,
                    "exactMinutes": round(minutes, 2),
                },
            },
        }
    )
