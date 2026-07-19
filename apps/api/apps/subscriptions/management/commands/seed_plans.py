"""Seed free/premium plans."""

from django.core.management.base import BaseCommand

from apps.subscriptions.services import ensure_plans


class Command(BaseCommand):
    help = "Ensure Free and Premium subscription plans exist"

    def handle(self, *args, **options):
        ensure_plans()
        self.stdout.write(self.style.SUCCESS("Plans ensured: free, premium"))
