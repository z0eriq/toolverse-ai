"""Seed ~30 programmatic SEO starter pages."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.programmatic_seo.models import ProgrammaticPage

STARTER_PAGES: list[dict] = [
    # best_of
    {
        "slug": "best/pdf-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "pdf-tools",
        "category_slug": "pdf",
        "title": {"en": "Best Free PDF Tools Online"},
        "description": {
            "en": "Compare the best free PDF tools — merge, split, compress, convert, and more."
        },
        "keyword": "best pdf tools",
        "related_tool_ids": ["pdf-merge", "pdf-split", "pdf-compress"],
    },
    {
        "slug": "best/image-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "image-tools",
        "category_slug": "image",
        "title": {"en": "Best Free Image Tools Online"},
        "description": {"en": "Resize, convert, compress, and edit images with free online tools."},
        "keyword": "best image tools",
        "related_tool_ids": ["image-resize", "image-compress", "color-converter"],
    },
    {
        "slug": "best/json-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "json-tools",
        "category_slug": "developer",
        "title": {"en": "Best Free JSON Tools Online"},
        "description": {"en": "Format, validate, and convert JSON with the best free developer tools."},
        "keyword": "best json tools",
        "related_tool_ids": ["json-formatter"],
    },
    {
        "slug": "best/developer-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "developer-tools",
        "category_slug": "developer",
        "title": {"en": "Best Free Developer Tools Online"},
        "description": {
            "en": "Essential free developer utilities — formatters, generators, converters, and more."
        },
        "keyword": "best developer tools",
        "related_tool_ids": ["json-formatter", "base64", "uuid"],
    },
    {
        "slug": "best/text-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "text-tools",
        "category_slug": "text",
        "title": {"en": "Best Free Text Tools Online"},
        "description": {"en": "Word counters, case converters, diff tools, and more text utilities."},
        "keyword": "best text tools",
        "related_tool_ids": [],
    },
    {
        "slug": "best/security-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "security-tools",
        "category_slug": "security",
        "title": {"en": "Best Free Security & Password Tools"},
        "description": {"en": "Generate strong passwords and check security with free online tools."},
        "keyword": "best password tools",
        "related_tool_ids": [],
    },
    # audience
    {
        "slug": "tools/for-students",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "students",
        "title": {"en": "Free Online Tools for Students"},
        "description": {
            "en": "PDF, writing, converters, and study helpers — free tools built for students."
        },
        "keyword": "tools for students",
        "related_tool_ids": [],
    },
    {
        "slug": "tools/for-developers",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "developers",
        "category_slug": "developer",
        "title": {"en": "Free Online Tools for Developers"},
        "description": {
            "en": "JSON, Base64, UUID, regex, and more free developer utilities in one place."
        },
        "keyword": "tools for developers",
        "related_tool_ids": ["json-formatter", "base64", "uuid"],
    },
    {
        "slug": "tools/for-marketers",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "marketers",
        "title": {"en": "Free Online Tools for Marketers"},
        "description": {
            "en": "Image, text, SEO helpers, and converters for modern marketing workflows."
        },
        "keyword": "tools for marketers",
        "related_tool_ids": [],
    },
    {
        "slug": "tools/for-designers",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "designers",
        "category_slug": "image",
        "title": {"en": "Free Online Tools for Designers"},
        "description": {"en": "Color converters, image tools, and design utilities — free forever."},
        "keyword": "tools for designers",
        "related_tool_ids": ["color-converter"],
    },
    {
        "slug": "tools/for-writers",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "writers",
        "category_slug": "text",
        "title": {"en": "Free Online Tools for Writers"},
        "description": {"en": "Word count, markdown, case convert, and writing helpers online."},
        "keyword": "tools for writers",
        "related_tool_ids": ["markdown-preview"],
    },
    # keyword / category pages
    {
        "slug": "json/json-formatter-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "json",
        "keyword": "json-formatter",
        "title": {"en": "JSON Formatter Online — Free & Instant"},
        "description": {
            "en": "Pretty-print, validate, and minify JSON in your browser. Free JSON formatter online."
        },
        "related_tool_ids": ["json-formatter"],
    },
    {
        "slug": "password/strong-password-generator",
        "path_pattern": "{category}/{keyword}",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "password",
        "keyword": "strong-password-generator",
        "title": {"en": "Strong Password Generator Online"},
        "description": {
            "en": "Generate secure, random passwords instantly. Free strong password generator."
        },
        "related_tool_ids": [],
    },
    {
        "slug": "base64/base64-encode-decode-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "base64",
        "keyword": "base64-encode-decode",
        "title": {"en": "Base64 Encode Decode Online"},
        "description": {"en": "Encode and decode Base64 strings and files for free online."},
        "related_tool_ids": ["base64"],
    },
    {
        "slug": "uuid/uuid-generator-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "uuid",
        "keyword": "uuid-generator",
        "title": {"en": "UUID Generator Online"},
        "description": {"en": "Generate UUID v4 identifiers instantly — free UUID generator online."},
        "related_tool_ids": ["uuid"],
    },
    {
        "slug": "color/hex-to-rgb-converter",
        "path_pattern": "{category}/{keyword}",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "color",
        "keyword": "hex-to-rgb-converter",
        "title": {"en": "HEX to RGB Color Converter"},
        "description": {"en": "Convert HEX colors to RGB and more. Free online color converter."},
        "related_tool_ids": ["color-converter"],
    },
    {
        "slug": "markdown/markdown-preview-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "markdown",
        "keyword": "markdown-preview",
        "title": {"en": "Markdown Preview Online"},
        "description": {"en": "Live markdown preview and editor in your browser — free forever."},
        "related_tool_ids": ["markdown-preview"],
    },
    {
        "slug": "pdf/merge-pdf-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "pdf",
        "keyword": "merge-pdf",
        "title": {"en": "Merge PDF Online Free"},
        "description": {"en": "Combine multiple PDF files into one. Free merge PDF online tool."},
        "related_tool_ids": ["pdf-merge"],
    },
    {
        "slug": "pdf/compress-pdf-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "pdf",
        "keyword": "compress-pdf",
        "title": {"en": "Compress PDF Online Free"},
        "description": {"en": "Reduce PDF file size without losing quality. Free compress PDF tool."},
        "related_tool_ids": ["pdf-compress"],
    },
    {
        "slug": "image/resize-image-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "image",
        "keyword": "resize-image",
        "title": {"en": "Resize Image Online Free"},
        "description": {"en": "Resize images by pixels or percent. Free online image resizer."},
        "related_tool_ids": ["image-resize"],
    },
    {
        "slug": "text/word-counter-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "text",
        "keyword": "word-counter",
        "title": {"en": "Word Counter Online"},
        "description": {"en": "Count words, characters, and sentences instantly. Free word counter."},
        "related_tool_ids": [],
    },
    {
        "slug": "hash/sha256-hash-generator",
        "path_pattern": "{category}/{keyword}",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "hash",
        "keyword": "sha256-hash-generator",
        "title": {"en": "SHA256 Hash Generator Online"},
        "description": {"en": "Generate SHA-256 hashes from text or files. Free hash generator."},
        "related_tool_ids": [],
    },
    {
        "slug": "qr/qr-code-generator-online",
        "path_pattern": "{category}/{keyword}-online",
        "page_type": ProgrammaticPage.PageType.KEYWORD,
        "category_slug": "qr",
        "keyword": "qr-code-generator",
        "title": {"en": "QR Code Generator Online"},
        "description": {"en": "Create QR codes for URLs, text, and more. Free QR code generator."},
        "related_tool_ids": [],
    },
    # category hubs
    {
        "slug": "hub/pdf",
        "path_pattern": "hub/{category}",
        "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
        "category_slug": "pdf",
        "title": {"en": "PDF Tools Hub"},
        "description": {"en": "All free PDF tools — merge, split, compress, convert, and more."},
        "keyword": "pdf tools",
        "related_tool_ids": [],
    },
    {
        "slug": "hub/developer",
        "path_pattern": "hub/{category}",
        "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
        "category_slug": "developer",
        "title": {"en": "Developer Tools Hub"},
        "description": {"en": "Browse all free developer tools on ToolVerse AI."},
        "keyword": "developer tools hub",
        "related_tool_ids": [],
    },
    {
        "slug": "hub/image",
        "path_pattern": "hub/{category}",
        "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
        "category_slug": "image",
        "title": {"en": "Image Tools Hub"},
        "description": {"en": "Free image resize, compress, convert, and color tools."},
        "keyword": "image tools hub",
        "related_tool_ids": [],
    },
    {
        "slug": "hub/text",
        "path_pattern": "hub/{category}",
        "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
        "category_slug": "text",
        "title": {"en": "Text Tools Hub"},
        "description": {"en": "Free text utilities for writers, students, and professionals."},
        "keyword": "text tools hub",
        "related_tool_ids": [],
    },
    {
        "slug": "hub/security",
        "path_pattern": "hub/{category}",
        "page_type": ProgrammaticPage.PageType.CATEGORY_HUB,
        "category_slug": "security",
        "title": {"en": "Security Tools Hub"},
        "description": {"en": "Password generators, hash tools, and security utilities."},
        "keyword": "security tools hub",
        "related_tool_ids": [],
    },
    {
        "slug": "best/converter-tools",
        "path_pattern": "best/{topic}",
        "page_type": ProgrammaticPage.PageType.BEST_OF,
        "topic": "converter-tools",
        "title": {"en": "Best Free Converter Tools Online"},
        "description": {"en": "Unit, color, encoding, and file converters — free and fast."},
        "keyword": "best converter tools",
        "related_tool_ids": ["color-converter", "base64"],
    },
    {
        "slug": "tools/for-freelancers",
        "path_pattern": "tools/for-{audience}",
        "page_type": ProgrammaticPage.PageType.AUDIENCE,
        "audience": "freelancers",
        "title": {"en": "Free Online Tools for Freelancers"},
        "description": {
            "en": "Productivity, PDF, image, and developer tools for freelancers — no signup."
        },
        "keyword": "tools for freelancers",
        "related_tool_ids": [],
    },
]


class Command(BaseCommand):
    help = "Seed programmatic SEO starter pages (~30)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--publish",
            action="store_true",
            default=True,
            help="Mark seeded pages as published (default: true)",
        )
        parser.add_argument(
            "--draft",
            action="store_true",
            help="Seed as draft instead of published",
        )

    def handle(self, *args, **options):
        status = (
            ProgrammaticPage.Status.DRAFT
            if options.get("draft")
            else ProgrammaticPage.Status.PUBLISHED
        )
        created = 0
        updated = 0
        for raw in STARTER_PAGES:
            slug = raw["slug"]
            defaults = {
                "path_pattern": raw.get("path_pattern", ""),
                "title": raw.get("title", {}),
                "description": raw.get("description", {}),
                "body": raw.get(
                    "body",
                    {
                        "en": f"<p>{(raw.get('description') or {}).get('en', '')}</p>"
                    },
                ),
                "page_type": raw["page_type"],
                "topic": raw.get("topic", ""),
                "category_slug": raw.get("category_slug", ""),
                "audience": raw.get("audience", ""),
                "keyword": raw.get("keyword", ""),
                "status": status,
                "related_tool_ids": raw.get("related_tool_ids", []),
                "seo_title": raw.get("seo_title") or raw.get("title", {}),
                "seo_description": raw.get("seo_description") or raw.get("description", {}),
                "seo_keywords": raw.get("seo_keywords")
                or ([raw["keyword"]] if raw.get("keyword") else []),
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
                f"Programmatic pages seeded: {created} created, {updated} updated "
                f"(total starters={len(STARTER_PAGES)}, status={status})"
            )
        )
