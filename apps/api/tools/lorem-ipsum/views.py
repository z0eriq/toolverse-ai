"""Lorem ipsum text generation API."""

from __future__ import annotations

import random

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

_WORDS = (
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
    "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
    "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
    "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
    "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
    "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
    "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
    "deserunt", "mollit", "anim", "id", "est", "laborum", "curabitur", "pretium",
    "tincidunt", "lacus", "aenean", "pulvinar", "viverra", "phasellus", "viverra",
    "nulla", "ut", "metus", "varius", "laoreet", "quisque", "rutrum", "aenean",
    "imperdiet", "etiam", "ultricies", "nisi", "vel", "augue",
)

_MAX_COUNT = 100


class ToolThrottle(AnonRateThrottle):
    scope = "tool"


def _error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response(
        {"success": False, "error": {"status_code": status_code, "message": message}},
        status=status_code,
    )


def _sentence(rng: random.Random, word_count: int | None = None) -> str:
    n = word_count or rng.randint(6, 14)
    words = [rng.choice(_WORDS) for _ in range(n)]
    words[0] = words[0].capitalize()
    return " ".join(words) + "."


def _paragraph(rng: random.Random, sentences: int | None = None) -> str:
    n = sentences or rng.randint(3, 6)
    return " ".join(_sentence(rng) for _ in range(n))


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ToolThrottle])
def lorem_ipsum_view(request) -> Response:
    """
    Body: {
      "units": "paragraphs" | "sentences" | "words",
      "count": 1..100,
      "startWithLorem"?: bool,
      "seed"?: int
    }
    """
    payload = request.data if isinstance(request.data, dict) else {}
    units = str(payload.get("units", "paragraphs")).lower().strip()
    if units not in {"paragraphs", "sentences", "words"}:
        return _error("units must be one of: paragraphs, sentences, words.")

    try:
        count = int(payload.get("count", 3 if units == "paragraphs" else 5))
    except (TypeError, ValueError):
        return _error("count must be an integer.")
    if count < 1 or count > _MAX_COUNT:
        return _error(f"count must be between 1 and {_MAX_COUNT}.")

    start_with_lorem = bool(payload.get("startWithLorem", payload.get("start_with_lorem", True)))
    seed = payload.get("seed")
    rng = random.Random(int(seed) if seed is not None else None)

    if units == "words":
        words = [rng.choice(_WORDS) for _ in range(count)]
        if start_with_lorem and count >= 2:
            words[0], words[1] = "Lorem", "ipsum"
        elif start_with_lorem and count == 1:
            words[0] = "Lorem"
        text = " ".join(words)
        items = words
    elif units == "sentences":
        items = [_sentence(rng) for _ in range(count)]
        if start_with_lorem and items:
            rest = items[0].split(" ", 2)
            if len(rest) >= 3:
                items[0] = f"Lorem ipsum {rest[2]}"
            else:
                items[0] = "Lorem ipsum dolor sit amet."
        text = " ".join(items)
    else:
        items = [_paragraph(rng) for _ in range(count)]
        if start_with_lorem and items:
            items[0] = (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " + items[0]
            )
        text = "\n\n".join(items)

    return Response(
        {
            "success": True,
            "data": {
                "units": units,
                "count": count,
                "text": text,
                "items": items if units != "words" else None,
            },
        }
    )
