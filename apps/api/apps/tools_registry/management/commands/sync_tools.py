from django.core.management.base import BaseCommand

from apps.tools_registry.discovery import sync_tools_from_filesystem


class Command(BaseCommand):
    help = "Discover tool manifests on disk and sync Category/Tool records"

    def handle(self, *args, **options):
        result = sync_tools_from_filesystem()
        self.stdout.write(self.style.SUCCESS(f"Synced tools: {result}"))
