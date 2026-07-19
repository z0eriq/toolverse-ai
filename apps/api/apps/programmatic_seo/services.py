"""Programmatic SEO batch generation helpers."""

from __future__ import annotations

from typing import Any

from django.utils.text import slugify

from apps.programmatic_seo.models import ProgrammaticPage

# Seed topics per page type — used when no keyword/tool data is available.
_BATCH_TOPICS: dict[str, list[dict[str, str]]] = {
    ProgrammaticPage.PageType.USE_CASE: [
        {"topic": "compress-pdf-for-email", "title": "Compress PDF for Email"},
        {"topic": "convert-images-for-web", "title": "Convert Images for Web"},
        {"topic": "format-json-for-apis", "title": "Format JSON for APIs"},
        {"topic": "generate-passwords-for-teams", "title": "Generate Passwords for Teams"},
        {"topic": "merge-pdfs-for-reports", "title": "Merge PDFs for Reports"},
        {"topic": "resize-photos-for-social", "title": "Resize Photos for Social"},
        {"topic": "validate-json-for-debugging", "title": "Validate JSON for Debugging"},
        {"topic": "split-pdfs-for-sharing", "title": "Split PDFs for Sharing"},
        {"topic": "encode-base64-for-data-uris", "title": "Encode Base64 for Data URIs"},
        {"topic": "count-words-for-essays", "title": "Count Words for Essays"},
        {"topic": "hash-files-for-integrity", "title": "Hash Files for Integrity"},
        {"topic": "minify-css-for-performance", "title": "Minify CSS for Performance"},
    ],
    ProgrammaticPage.PageType.INDUSTRY: [
        {"topic": "education", "title": "Free Online Tools for Education"},
        {"topic": "healthcare", "title": "Free Online Tools for Healthcare"},
        {"topic": "legal", "title": "Free Online Tools for Legal Teams"},
        {"topic": "marketing", "title": "Free Online Tools for Marketing"},
        {"topic": "finance", "title": "Free Online Tools for Finance"},
        {"topic": "ecommerce", "title": "Free Online Tools for Ecommerce"},
        {"topic": "real-estate", "title": "Free Online Tools for Real Estate"},
        {"topic": "startups", "title": "Free Online Tools for Startups"},
        {"topic": "agencies", "title": "Free Online Tools for Agencies"},
        {"topic": "freelancers", "title": "Free Online Tools for Freelancers"},
    ],
    ProgrammaticPage.PageType.COMPARISON: [
        {"topic": "pdf-merge-vs-pdf-split", "title": "PDF Merge vs PDF Split"},
        {"topic": "json-formatter-vs-validator", "title": "JSON Formatter vs Validator"},
        {"topic": "image-compress-vs-resize", "title": "Image Compress vs Resize"},
        {"topic": "base64-encode-vs-decode", "title": "Base64 Encode vs Decode"},
        {"topic": "uuid-vs-nanoid", "title": "UUID vs NanoID Generators"},
        {"topic": "md5-vs-sha256", "title": "MD5 vs SHA256 Hash Tools"},
        {"topic": "word-counter-vs-character-counter", "title": "Word vs Character Counter"},
        {"topic": "color-picker-vs-converter", "title": "Color Picker vs Converter"},
        {"topic": "qr-vs-barcode", "title": "QR Code vs Barcode Generators"},
        {"topic": "csv-to-json-vs-json-to-csv", "title": "CSV↔JSON Conversion Tools"},
    ],
    ProgrammaticPage.PageType.TUTORIAL: [
        {"topic": "how-to-merge-pdfs", "title": "How to Merge PDFs Online"},
        {"topic": "how-to-compress-images", "title": "How to Compress Images for Web"},
        {"topic": "how-to-format-json", "title": "How to Format JSON Correctly"},
        {"topic": "how-to-generate-uuids", "title": "How to Generate UUIDs"},
        {"topic": "how-to-encode-base64", "title": "How to Encode Base64 Strings"},
        {"topic": "how-to-resize-photos", "title": "How to Resize Photos Free"},
        {"topic": "how-to-split-pdf", "title": "How to Split a PDF File"},
        {"topic": "how-to-convert-heic", "title": "How to Convert HEIC to JPG"},
        {"topic": "how-to-hash-files", "title": "How to Hash Files for Integrity"},
        {"topic": "how-to-create-qr-codes", "title": "How to Create QR Codes Online"},
        {"topic": "how-to-minify-css", "title": "How to Minify CSS"},
        {"topic": "how-to-validate-json", "title": "How to Validate JSON Schemas"},
    ],
    ProgrammaticPage.PageType.TOOL: [
        {"topic": "pdf-merge", "title": "PDF Merge Tool Landing"},
        {"topic": "pdf-compress", "title": "PDF Compress Tool Landing"},
        {"topic": "image-resize", "title": "Image Resize Tool Landing"},
        {"topic": "json-formatter", "title": "JSON Formatter Tool Landing"},
        {"topic": "password-generator", "title": "Password Generator Tool Landing"},
        {"topic": "qr-code", "title": "QR Code Tool Landing"},
        {"topic": "word-counter", "title": "Word Counter Tool Landing"},
        {"topic": "base64", "title": "Base64 Tool Landing"},
        {"topic": "uuid-generator", "title": "UUID Generator Tool Landing"},
        {"topic": "color-picker", "title": "Color Picker Tool Landing"},
        {"topic": "csv-to-json", "title": "CSV to JSON Tool Landing"},
        {"topic": "hash-generator", "title": "Hash Generator Tool Landing"},
    ],
}


def _prefix_for(page_type: str) -> str:
    return {
        ProgrammaticPage.PageType.USE_CASE: "use",
        ProgrammaticPage.PageType.INDUSTRY: "industry",
        ProgrammaticPage.PageType.COMPARISON: "compare",
        ProgrammaticPage.PageType.BEST_OF: "best",
        ProgrammaticPage.PageType.KEYWORD: "kw",
        ProgrammaticPage.PageType.AUDIENCE: "tools/for",
        ProgrammaticPage.PageType.CATEGORY_HUB: "hub",
        ProgrammaticPage.PageType.AUTHORITY: "guides",
        ProgrammaticPage.PageType.TUTORIAL: "tutorial",
        ProgrammaticPage.PageType.TOOL: "tools",
    }.get(page_type, page_type)


# Kind aliases accepted by generate_landing_batch
KIND_TO_PAGE_TYPE: dict[str, str] = {
    "tool": ProgrammaticPage.PageType.TOOL,
    "tutorial": ProgrammaticPage.PageType.TUTORIAL,
    "comparison": ProgrammaticPage.PageType.COMPARISON,
    "industry": ProgrammaticPage.PageType.INDUSTRY,
    "use_case": ProgrammaticPage.PageType.USE_CASE,
    "use-case": ProgrammaticPage.PageType.USE_CASE,
    "authority": ProgrammaticPage.PageType.AUTHORITY,
    "best_of": ProgrammaticPage.PageType.BEST_OF,
}


def generate_landing_batch(
    *,
    kinds: list[str],
    limit: int = 20,
    locale: str = "en",
    publish: bool = False,
) -> dict[str, Any]:
    """
    Generate draft ProgrammaticPages across multiple kinds.
    Never publishes unless publish=True.
    """
    limit = max(1, min(int(limit or 20), 200))
    per_kind = max(1, limit // max(len(kinds), 1))
    remainder = limit - (per_kind * len(kinds))
    results: list[dict[str, Any]] = []
    total_created = 0
    all_slugs: list[str] = []

    for i, kind in enumerate(kinds):
        key = kind.strip().lower()
        page_type = KIND_TO_PAGE_TYPE.get(key) or key
        batch_limit = per_kind + (1 if i < remainder else 0)
        result = generate_programmatic_batch(
            page_type=page_type,
            limit=batch_limit,
            locale=locale,
            publish=publish,
        )
        results.append(result)
        total_created += int(result.get("created") or 0)
        all_slugs.extend(result.get("slugs") or [])

    status = (
        ProgrammaticPage.Status.PUBLISHED if publish else ProgrammaticPage.Status.DRAFT
    )
    return {
        "created": total_created,
        "status": status,
        "kinds": kinds,
        "slugs": all_slugs,
        "batches": results,
    }



def generate_programmatic_batch(
    *,
    page_type: str,
    limit: int = 10,
    locale: str = "en",
    publish: bool = False,
) -> dict[str, Any]:
    """
    Create unique ProgrammaticPage rows for the given type.

    Default status is draft — never publish unless publish=True.
    """
    topics = list(_BATCH_TOPICS.get(page_type) or [])
    if not topics:
        # Fallback synthetic topics for other types
        topics = [
            {"topic": f"topic-{i}", "title": f"{page_type.replace('_', ' ').title()} {i}"}
            for i in range(1, max(limit, 1) + 5)
        ]

    status = (
        ProgrammaticPage.Status.PUBLISHED if publish else ProgrammaticPage.Status.DRAFT
    )
    prefix = _prefix_for(page_type)
    created = 0
    skipped = 0
    slugs: list[str] = []

    for item in topics:
        if created >= limit:
            break
        topic = slugify(item["topic"])[:80] or f"item-{created + 1}"
        slug = f"{prefix}/{topic}"
        if ProgrammaticPage.objects.filter(slug=slug).exists():
            # Ensure uniqueness with suffix
            n = 2
            candidate = f"{slug}-{n}"
            while ProgrammaticPage.objects.filter(slug=candidate).exists():
                n += 1
                candidate = f"{slug}-{n}"
            slug = candidate

        title_text = item.get("title") or topic.replace("-", " ").title()
        title = {locale: title_text, "en": title_text}
        description = {
            locale: f"{title_text} — free online tools on ToolVerse AI.",
            "en": f"{title_text} — free online tools on ToolVerse AI.",
        }
        ProgrammaticPage.objects.create(
            slug=slug,
            path_pattern=f"{prefix}/{{topic}}",
            title=title,
            description=description,
            body={locale: f"# {title_text}\n\nProgrammatic page draft.\n"},
            page_type=page_type,
            topic=topic,
            keyword=title_text.lower(),
            status=status,
            seo_title=title,
            seo_description=description,
        )
        slugs.append(slug)
        created += 1

    return {
        "created": created,
        "skipped": skipped,
        "status": status,
        "page_type": page_type,
        "slugs": slugs,
    }
