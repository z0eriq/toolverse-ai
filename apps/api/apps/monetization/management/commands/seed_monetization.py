from django.core.management.base import BaseCommand

from apps.monetization.seed import ensure_default_placements


class Command(BaseCommand):
    help = "Seed default AdPlacement rows"

    def handle(self, *args, **options):
        created = ensure_default_placements()
        self.stdout.write(self.style.SUCCESS(f"seed_monetization: created={created}"))
