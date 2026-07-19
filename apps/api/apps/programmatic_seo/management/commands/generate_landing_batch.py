"""Batch-generate landing pages across multiple kinds (draft by default)."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.programmatic_seo.models import ProgrammaticPage
from apps.programmatic_seo.services import KIND_TO_PAGE_TYPE, generate_landing_batch


class Command(BaseCommand):
    help = (
        "Generate landing ProgrammaticPages for kinds "
        "tool,tutorial,comparison,industry,use_case (draft unless --publish)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--kinds",
            default="tool,tutorial,comparison,industry,use_case",
            help="Comma-separated kinds",
        )
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--locale", default="en")
        parser.add_argument(
            "--publish",
            action="store_true",
            default=False,
            help="Publish pages (default: draft — never auto-publish)",
        )

    def handle(self, *args, **options):
        kinds = [k.strip() for k in str(options["kinds"]).split(",") if k.strip()]
        if not kinds:
            raise CommandError("Provide at least one kind via --kinds")
        valid = set(KIND_TO_PAGE_TYPE) | {c.value for c in ProgrammaticPage.PageType}
        for kind in kinds:
            if kind.lower() not in valid and kind not in valid:
                raise CommandError(
                    f"Invalid kind '{kind}'. Choose from: {sorted(KIND_TO_PAGE_TYPE)}"
                )
        result = generate_landing_batch(
            kinds=kinds,
            limit=int(options["limit"]),
            locale=str(options["locale"])[:10],
            publish=bool(options["publish"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"generate_landing_batch: created={result['created']} "
                f"status={result['status']} kinds={kinds}"
            )
        )
