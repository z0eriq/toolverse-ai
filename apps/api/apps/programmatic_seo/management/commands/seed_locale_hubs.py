"""Seed ProgrammaticPage locale hub pages for each supported locale."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.common.locales import SUPPORTED_LOCALES
from apps.programmatic_seo.models import ProgrammaticPage

LOCALE_NAMES = {
    "en": "English",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "zh": "Chinese",
}


class Command(BaseCommand):
    help = "Seed locale hub ProgrammaticPage rows (locale-hub-{lang})"

    def handle(self, *args, **options):
        created = updated = 0
        for locale in SUPPORTED_LOCALES:
            name = LOCALE_NAMES.get(locale, locale.upper())
            slug = f"locale-hub-{locale}"
            title = {locale: f"ToolVerse AI — {name}", "en": f"ToolVerse AI — {name}"}
            description = {
                locale: f"Explore free online tools in {name}.",
                "en": f"Explore free online tools in {name}.",
            }
            defaults = {
                "path_pattern": "l/{lang}",
                "title": title,
                "description": description,
                "body": {
                    "en": f"<p>Language hub for {name} ({locale}).</p>",
                    locale: f"<p>Language hub for {name} ({locale}).</p>",
                },
                "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
                "topic": f"locale-{locale}",
                "category_slug": "",
                "audience": "",
                "keyword": f"online tools {name.lower()}",
                "status": ProgrammaticPage.Status.PUBLISHED,
                "related_tool_ids": [],
                "seo_title": title,
                "seo_description": description,
                "seo_keywords": [f"tools {locale}", f"online tools {name.lower()}"],
            }
            _, was_created = ProgrammaticPage.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Locale hubs created={created} updated={updated}")
        )
