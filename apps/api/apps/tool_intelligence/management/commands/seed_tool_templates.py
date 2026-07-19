"""Seed ~10 ToolTemplate rows for the Global Launch Engine."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.tool_intelligence.models import ToolTemplate

TEMPLATES: list[dict] = [
    {
        "slug": "pdf-ocr-extract",
        "category_slug": "pdf",
        "recipe": "pdf",
        "priority_weight": 1.2,
        "description": "Extract text from scanned PDFs via OCR.",
        "ui_schema": {
            "fields": [
                {"name": "file", "type": "file", "label": "PDF file", "accept": ".pdf"},
                {"name": "language", "type": "select", "label": "Language", "default": "en"},
            ]
        },
        "pipeline": [{"type": "transform", "op": "pdf_ocr", "input": "file", "output": "text"}],
    },
    {
        "slug": "image-background-remover",
        "category_slug": "images",
        "recipe": "image",
        "priority_weight": 1.4,
        "description": "Remove image backgrounds automatically.",
        "ui_schema": {
            "fields": [{"name": "image", "type": "file", "label": "Image", "accept": "image/*"}]
        },
        "pipeline": [
            {"type": "transform", "op": "remove_bg", "input": "image", "output": "result"}
        ],
    },
    {
        "slug": "ai-rewrite-assistant",
        "category_slug": "ai",
        "recipe": "ai",
        "priority_weight": 1.5,
        "description": "Rewrite text for clarity, tone, or length with AI.",
        "ui_schema": {
            "fields": [
                {"name": "text", "type": "textarea", "label": "Text"},
                {"name": "tone", "type": "select", "label": "Tone", "default": "neutral"},
            ]
        },
        "pipeline": [{"type": "ai", "prompt": "Rewrite: {{text}}", "output": "result"}],
    },
    {
        "slug": "jwt-debugger-pro",
        "category_slug": "developer",
        "recipe": "developer",
        "priority_weight": 1.1,
        "description": "Decode and inspect JWT headers and payloads.",
        "ui_schema": {"fields": [{"name": "token", "type": "textarea", "label": "JWT"}]},
        "pipeline": [{"type": "transform", "op": "jwt_decode", "input": "token", "output": "result"}],
    },
    {
        "slug": "mortgage-calculator",
        "category_slug": "calculators",
        "recipe": "calculator",
        "priority_weight": 1.0,
        "description": "Estimate monthly mortgage payments.",
        "ui_schema": {
            "fields": [
                {"name": "principal", "type": "number", "label": "Principal"},
                {"name": "rate", "type": "number", "label": "Annual rate %"},
                {"name": "years", "type": "number", "label": "Years"},
            ]
        },
        "pipeline": [
            {"type": "transform", "op": "mortgage", "input": "principal", "output": "payment"}
        ],
    },
    {
        "slug": "markdown-to-html",
        "category_slug": "text",
        "recipe": "generic",
        "priority_weight": 0.9,
        "description": "Convert Markdown to clean HTML.",
        "ui_schema": {"fields": [{"name": "markdown", "type": "textarea", "label": "Markdown"}]},
        "pipeline": [
            {"type": "transform", "op": "md_to_html", "input": "markdown", "output": "html"}
        ],
    },
    {
        "slug": "color-palette-generator",
        "category_slug": "design",
        "recipe": "generic",
        "priority_weight": 1.0,
        "description": "Generate harmonious color palettes from a seed color.",
        "ui_schema": {
            "fields": [{"name": "hex", "type": "text", "label": "Seed HEX", "default": "#2563eb"}]
        },
        "pipeline": [
            {"type": "transform", "op": "palette", "input": "hex", "output": "colors"}
        ],
    },
    {
        "slug": "unit-converter-pro",
        "category_slug": "converters",
        "recipe": "generic",
        "priority_weight": 0.95,
        "description": "Convert length, weight, temperature, and more.",
        "ui_schema": {
            "fields": [
                {"name": "value", "type": "number", "label": "Value"},
                {"name": "from_unit", "type": "text", "label": "From"},
                {"name": "to_unit", "type": "text", "label": "To"},
            ]
        },
        "pipeline": [
            {"type": "transform", "op": "unit_convert", "input": "value", "output": "result"}
        ],
    },
    {
        "slug": "password-strength-analyzer",
        "category_slug": "security",
        "recipe": "generic",
        "priority_weight": 1.05,
        "description": "Analyze password strength and suggest improvements.",
        "ui_schema": {
            "fields": [{"name": "password", "type": "password", "label": "Password"}]
        },
        "pipeline": [
            {"type": "transform", "op": "password_score", "input": "password", "output": "score"}
        ],
    },
    {
        "slug": "csv-to-json-converter",
        "category_slug": "developer",
        "recipe": "developer",
        "priority_weight": 1.15,
        "description": "Convert CSV tables to JSON arrays.",
        "ui_schema": {"fields": [{"name": "csv", "type": "textarea", "label": "CSV"}]},
        "pipeline": [
            {"type": "transform", "op": "csv_to_json", "input": "csv", "output": "json"}
        ],
    },
]


class Command(BaseCommand):
    help = "Seed ~10 ToolTemplate definitions for opportunity scoring"

    def handle(self, *args, **options):
        created = updated = 0
        for raw in TEMPLATES:
            _, was_created = ToolTemplate.objects.update_or_create(
                slug=raw["slug"],
                defaults={
                    "category_slug": raw["category_slug"],
                    "recipe": raw["recipe"],
                    "ui_schema": raw.get("ui_schema") or {},
                    "pipeline": raw.get("pipeline") or [],
                    "priority_weight": raw.get("priority_weight", 1.0),
                    "description": raw.get("description", ""),
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Tool templates seeded: {created} created, {updated} updated "
                f"(total={len(TEMPLATES)})"
            )
        )
