"""Seed published authority pages for the Global Launch Engine."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.programmatic_seo.models import ProgrammaticPage

AUTHORITY_PAGES: list[dict] = [
    {
        "slug": "best-ai-tools",
        "title": {"en": "Best AI Tools Online"},
        "description": {
            "en": "Curated best AI tools for writing, coding, productivity, and creativity — free to try."
        },
        "keyword": "best ai tools",
        "category_slug": "ai",
        "topic": "ai-tools",
    },
    {
        "slug": "free-tools-for-students",
        "title": {"en": "Free Tools for Students"},
        "description": {
            "en": "PDF, writing, converters, and study helpers — free online tools built for students."
        },
        "keyword": "free tools for students",
        "audience": "students",
    },
    {
        "slug": "tools-for-developers",
        "title": {"en": "Tools for Developers"},
        "description": {
            "en": "JSON, Base64, UUID, hashing, and developer utilities — free and fast."
        },
        "keyword": "tools for developers",
        "category_slug": "developer",
        "audience": "developers",
    },
    {
        "slug": "productivity-tools",
        "title": {"en": "Productivity Tools"},
        "description": {
            "en": "Boost focus and throughput with free productivity tools on ToolVerse AI."
        },
        "keyword": "productivity tools",
        "topic": "productivity",
    },
]


class Command(BaseCommand):
    help = "Seed published authority programmatic pages"

    def handle(self, *args, **options):
        created = updated = 0
        for raw in AUTHORITY_PAGES:
            slug = raw["slug"]
            defaults = {
                "path_pattern": "authority/{slug}",
                "title": raw["title"],
                "description": raw["description"],
                "body": {
                    "en": f"<p>{raw['description']['en']}</p><p>Explore related tools on ToolVerse AI.</p>"
                },
                "page_type": ProgrammaticPage.PageType.AUTHORITY,
                "topic": raw.get("topic", ""),
                "category_slug": raw.get("category_slug", ""),
                "audience": raw.get("audience", ""),
                "keyword": raw.get("keyword", ""),
                "status": ProgrammaticPage.Status.PUBLISHED,
                "related_tool_ids": raw.get("related_tool_ids", []),
                "seo_title": raw["title"],
                "seo_description": raw["description"],
                "seo_keywords": [raw["keyword"]] if raw.get("keyword") else [],
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
            self.style.SUCCESS(
                f"Authority pages seeded: {created} created, {updated} updated "
                f"(total={len(AUTHORITY_PAGES)})"
            )
        )
