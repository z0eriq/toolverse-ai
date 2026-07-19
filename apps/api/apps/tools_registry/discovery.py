from __future__ import annotations

import importlib
import json
import logging
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import transaction

from apps.tools_registry.models import Category, Tool

logger = logging.getLogger("toolverse.tools")

CATEGORY_DEFAULTS: dict[str, dict[str, Any]] = {
    "developer": {
        "name": {"en": "Developer", "ar": "مطور"},
        "description": {
            "en": "JSON, encoding, hashing, JWT, and developer utilities",
            "ar": "أدوات JSON والترميز والتجزئة وJWT للمطورين",
        },
        "order": 1,
    },
    "text": {
        "name": {"en": "Text", "ar": "نص"},
        "description": {
            "en": "Writing helpers, counters, and markdown tools",
            "ar": "أدوات الكتابة والعدادات وMarkdown",
        },
        "order": 2,
    },
    "design": {
        "name": {"en": "Design", "ar": "تصميم"},
        "description": {
            "en": "Colors, contrast, and design utilities",
            "ar": "الألوان والتباين وأدوات التصميم",
        },
        "order": 3,
    },
    "converters": {
        "name": {"en": "Converters", "ar": "محولات"},
        "description": {
            "en": "Format and unit converters",
            "ar": "محولات الصيغ والوحدات",
        },
        "order": 4,
    },
    "security": {
        "name": {"en": "Security", "ar": "أمان"},
        "description": {
            "en": "Security and cryptography helpers",
            "ar": "أدوات الأمان والتشفير",
        },
        "order": 5,
    },
    "ai": {
        "name": {"en": "AI", "ar": "ذكاء اصطناعي"},
        "description": {
            "en": "AI-powered productivity tools",
            "ar": "أدوات الإنتاجية المدعومة بالذكاء الاصطناعي",
        },
        "order": 6,
    },
    "pdf": {
        "name": {"en": "PDF", "ar": "PDF"},
        "description": {
            "en": "PDF merge, split, compress, and convert utilities",
            "ar": "دمج وتقسيم وضغط وتحويل ملفات PDF",
        },
        "order": 7,
    },
    "images": {
        "name": {"en": "Images", "ar": "صور"},
        "description": {
            "en": "Image compress, resize, convert, and creative tools",
            "ar": "ضغط وتغيير حجم وتحويل الصور وأدوات إبداعية",
        },
        "order": 8,
    },
    "calculators": {
        "name": {"en": "Calculators", "ar": "حاسبات"},
        "description": {
            "en": "Finance, math, health, and unit calculators",
            "ar": "حاسبات مالية ورياضية وصحية ووحدات",
        },
        "order": 9,
    },
}


def discover_manifest_paths() -> list[Path]:
    tools_dir = Path(settings.TOOLS_DIR)
    if not tools_dir.exists():
        return []
    return sorted(tools_dir.glob("*/manifest.json"))


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    required = ("id", "slug", "category", "name", "description", "version", "seo", "capabilities")
    for key in required:
        if key not in data:
            raise ValueError(f"Manifest {path} missing required key: {key}")
    return data


@transaction.atomic
def sync_tools_from_filesystem() -> dict[str, int]:
    """Scan tools/*/manifest.json and upsert Category + Tool rows."""
    created = updated = skipped = 0
    seen_ids: set[str] = set()

    for slug, meta in CATEGORY_DEFAULTS.items():
        Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": meta["name"],
                "description": meta["description"],
                "order": meta["order"],
                "is_active": True,
            },
        )

    for path in discover_manifest_paths():
        try:
            manifest = load_manifest(path)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load manifest %s: %s", path, exc)
            skipped += 1
            continue

        tool_id = manifest["id"]
        seen_ids.add(tool_id)
        category, _ = Category.objects.get_or_create(
            slug=manifest["category"],
            defaults={
                "name": {"en": manifest["category"].title()},
                "description": {"en": ""},
                "order": 99,
            },
        )
        seo = manifest.get("seo") or {}
        defaults = {
            "slug": manifest["slug"],
            "category": category,
            "name": manifest["name"],
            "description": manifest["description"],
            "version": manifest["version"],
            "premium": bool(manifest.get("premium", False)),
            "adsense_slot": manifest.get("adsenseSlot", "sidebar"),
            "seo_title": seo.get("title", manifest["name"]),
            "seo_description": seo.get("description", manifest["description"]),
            "seo_keywords": seo.get("keywords", []),
            "schema_type": manifest.get("schemaType", "WebApplication"),
            "capabilities": manifest.get("capabilities", []),
            "icon": manifest.get("icon", ""),
            "order": int(manifest.get("order", 0)),
            "is_active": True,
            "source": Tool.Source.FILESYSTEM,
            "faq": manifest.get("faq", []),
            "howto_steps": manifest.get("howto") or manifest.get("howto_steps", []),
            "related_slugs": manifest.get("relatedSlugs") or manifest.get("related_slugs", []),
        }
        tool, was_created = Tool.objects.update_or_create(tool_id=tool_id, defaults=defaults)
        tool.rebuild_search_document()
        tool.save(update_fields=["search_document", "updated_at"])
        if was_created:
            created += 1
        else:
            updated += 1

    # Soft-deactivate filesystem tools removed from disk (never touch dynamic tools)
    deactivated = (
        Tool.objects.filter(source=Tool.Source.FILESYSTEM, is_active=True)
        .exclude(tool_id__in=seen_ids)
        .update(is_active=False)
        if seen_ids is not None
        else 0
    )

    from apps.tools_registry.publish import sync_dynamic_tools

    dynamic_stats = sync_dynamic_tools()

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "deactivated": deactivated,
        "total": len(seen_ids),
        "dynamic": dynamic_stats,
    }


def load_tool_plugins() -> dict[str, Any]:
    """Import ToolPlugin from each tools.<id> package if present."""
    plugins: dict[str, Any] = {}
    tools_dir = Path(settings.TOOLS_DIR)
    if not tools_dir.exists():
        return plugins

    # Registers hyphenated-package meta path finder (tools.json-formatter, etc.)
    importlib.import_module("tools")

    for child in tools_dir.iterdir():
        if not child.is_dir() or child.name.startswith("_") or child.name == "base.py":
            continue
        if not (child / "__init__.py").exists() and not (child / "manifest.json").exists():
            continue
        module_name = f"tools.{child.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            logger.debug("No importable plugin for %s: %s", child.name, exc)
            continue
        plugin = getattr(module, "plugin", None) or getattr(module, "ToolPlugin", None)
        if plugin is not None:
            plugins[child.name] = plugin if not isinstance(plugin, type) else plugin()
    return plugins
