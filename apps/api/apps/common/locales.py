"""Supported UI/content locales for ToolVerse AI (frontend i18n + content factory).

Backend messages stay English; these codes drive content locale fields and
programmatic SEO. Keep in sync with apps/web next-intl locales.
"""

from __future__ import annotations

SUPPORTED_LOCALES: tuple[str, ...] = (
    "en",
    "ar",
    "es",
    "fr",
    "de",
    "pt",
    "zh",
)

DEFAULT_LOCALE = "en"


def is_supported_locale(code: str) -> bool:
    return (code or "").lower().split("-")[0] in SUPPORTED_LOCALES
