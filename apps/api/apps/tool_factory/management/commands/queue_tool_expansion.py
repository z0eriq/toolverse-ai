"""Queue draft ToolSpec rows from the first-1000 expansion catalog."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.tool_factory.expansion import catalog_capacity_summary, queue_tool_expansion


class Command(BaseCommand):
    help = (
        "Create draft ToolSpec rows from expansion catalog "
        "(--category pdf|image|ai|calculators|developer|business --limit N). "
        "Never publishes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            required=True,
            help="Category key: pdf, image, ai, calculators, developer, business",
        )
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Print catalog capacity summary and exit",
        )

    def handle(self, *args, **options):
        if options.get("summary"):
            summary = catalog_capacity_summary()
            self.stdout.write(self.style.SUCCESS(str(summary)))
            return

        category = str(options["category"]).strip().lower()
        try:
            result = queue_tool_expansion(category=category, limit=int(options["limit"]))
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"queue_tool_expansion: category={result['category']} "
                f"created={result['created']} skipped={result['skipped']} "
                f"status={result['status']} (never published)"
            )
        )
