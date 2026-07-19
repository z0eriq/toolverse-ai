"""Generate packages/api-client TypeScript stub."""

from django.core.management.base import BaseCommand

from apps.marketplace.billing import generate_sdk


class Command(BaseCommand):
    help = "Write packages/api-client stub TypeScript SDK"

    def handle(self, *args, **options):
        result = generate_sdk()
        self.stdout.write(self.style.SUCCESS(f"Wrote SDK at {result['path']}"))
