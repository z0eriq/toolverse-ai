from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.workflows.models import WorkflowTemplate

TEMPLATES = [
    {
        "slug": "json-format-uppercase",
        "name": "JSON Format → Uppercase",
        "description": "Parse/format JSON text then uppercase the result.",
        "category": "developer",
        "steps": [
            {
                "type": "transform",
                "op": "json_format",
                "source": "input.text",
                "target": "output",
            },
            {
                "type": "transform",
                "op": "uppercase",
                "source": "output",
                "target": "output",
            },
        ],
    },
    {
        "slug": "base64-roundtrip",
        "name": "Base64 Encode → Decode",
        "description": "Encode text to base64 then decode back (demo chain).",
        "category": "developer",
        "steps": [
            {
                "type": "transform",
                "op": "base64_encode",
                "source": "input.text",
                "target": "vars.encoded",
            },
            {
                "type": "transform",
                "op": "base64_decode",
                "source": "vars.encoded",
                "target": "output",
            },
        ],
    },
    {
        "slug": "trim-word-count",
        "name": "Trim → Word Count",
        "description": "Trim whitespace then count words/chars.",
        "category": "text",
        "steps": [
            {"type": "transform", "op": "trim", "source": "input.text", "target": "output"},
            {"type": "transform", "op": "word_count", "source": "output", "target": "output"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed public WorkflowTemplate rows for Launch Scale workflows"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for item in TEMPLATES:
            _, was_created = WorkflowTemplate.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "category": item["category"],
                    "steps": item["steps"],
                    "is_public": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Workflow templates seeded (created={created}, updated={updated})")
        )
