"""Seed ~50 published DynamicToolDefinition starters from expansion fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.tools_registry.dynamic_models import DynamicToolDefinition
from apps.tools_registry.growth_models import ToolGrowthMeta
from apps.tools_registry.publish import publish_dynamic_tool

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "expansion_pack.json"


class Command(BaseCommand):
    help = "Load expansion_pack.json and publish DynamicToolDefinition tools"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional max number of tools to seed (0 = all)",
        )

    def handle(self, *args, **options):
        if not FIXTURE.exists():
            self.stderr.write(self.style.ERROR(f"Missing fixture: {FIXTURE}"))
            return

        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        limit = int(options.get("limit") or 0)
        if limit > 0:
            data = data[:limit]

        created = updated = published = 0
        for item in data:
            slug = item["slug"]
            defaults = {
                "category_slug": item.get("category") or "ai",
                "name": item.get("name") or {"en": slug},
                "description": item.get("description") or {"en": ""},
                "ui_schema": item.get("ui_schema") or {},
                "pipeline": item.get("pipeline") or [],
                "seo": item.get("seo") or {},
                "faq": item.get("faq") or [],
                "howto_steps": item.get("howto") or [],
                "capabilities": item.get("capabilities") or ["server"],
                "status": DynamicToolDefinition.Status.PUBLISHED,
            }
            definition, was_created = DynamicToolDefinition.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

            tool = publish_dynamic_tool(definition)
            tool.faq = definition.faq or []
            tool.howto_steps = definition.howto_steps or []
            tool.save(update_fields=["faq", "howto_steps", "updated_at"])

            if item.get("is_viral"):
                ToolGrowthMeta.objects.update_or_create(
                    tool=tool,
                    defaults={
                        "is_viral": True,
                        "share_text": item.get("share_text") or {},
                        "og_template": "viral",
                        "share_platforms": ["twitter", "linkedin", "copy"],
                    },
                )
            published += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_tool_expansion: created={created} updated={updated} published={published}"
            )
        )
