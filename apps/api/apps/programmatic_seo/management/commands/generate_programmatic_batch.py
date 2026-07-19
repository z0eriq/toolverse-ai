"""Batch-generate programmatic SEO pages (draft by default)."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.programmatic_seo.models import ProgrammaticPage
from apps.programmatic_seo.services import generate_programmatic_batch


class Command(BaseCommand):
    help = "Generate a batch of programmatic SEO pages (--type --limit --locale --publish)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            dest="page_type",
            default=ProgrammaticPage.PageType.USE_CASE,
            help="Page type: use_case|industry|comparison|best_of|keyword|...",
        )
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--locale", default="en")
        parser.add_argument(
            "--publish",
            action="store_true",
            default=False,
            help="Publish pages (default: draft)",
        )

    def handle(self, *args, **options):
        page_type = options["page_type"]
        valid = {c.value for c in ProgrammaticPage.PageType}
        if page_type not in valid:
            raise CommandError(f"Invalid --type {page_type}. Choose from: {sorted(valid)}")
        result = generate_programmatic_batch(
            page_type=page_type,
            limit=int(options["limit"]),
            locale=str(options["locale"])[:10],
            publish=bool(options["publish"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"created={result['created']} skipped={result['skipped']} "
                f"type={page_type} status={result['status']}"
            )
        )
