"""Export OpenAPI schema to apps/web/public/openapi.json."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Write OpenAPI schema JSON to apps/web/public/openapi.json"

    def handle(self, *args, **options):
        # apps/api is BASE_DIR; monorepo root is parents[1]
        api_dir = Path(settings.BASE_DIR)
        out = api_dir.parent / "web" / "public" / "openapi.json"
        out.parent.mkdir(parents=True, exist_ok=True)

        schema: dict
        try:
            from drf_spectacular.generators import SchemaGenerator

            generator = SchemaGenerator()
            schema = generator.get_schema(request=None, public=True) or {}
            if hasattr(schema, "copy"):
                schema = dict(schema)
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f"Spectacular failed ({exc}); writing stub"))
            schema = {
                "openapi": "3.0.3",
                "info": {
                    "title": "ToolVerse AI API",
                    "version": "1.0.0",
                    "description": "Stub schema — run with drf-spectacular for full export.",
                },
                "paths": {},
            }

        out.write_text(json.dumps(schema, indent=2, default=str), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote OpenAPI schema to {out}"))
