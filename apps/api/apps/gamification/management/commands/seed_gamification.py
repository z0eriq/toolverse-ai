from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.gamification.models import Badge

BADGES = [
    {
        "slug": "first_tool",
        "name": "First Tool",
        "description": "Ran your first tool",
        "icon": "spark",
        "points_required": 10,
    },
    {
        "slug": "power_user",
        "name": "Power User",
        "description": "Accumulated 500 lifetime points",
        "icon": "bolt",
        "points_required": 500,
    },
    {
        "slug": "reviewer",
        "name": "Reviewer",
        "description": "Submitted helpful reviews",
        "icon": "star",
        "points_required": 50,
    },
    {
        "slug": "referrer",
        "name": "Referrer",
        "description": "Qualified a successful referral",
        "icon": "users",
        "points_required": 100,
    },
]


class Command(BaseCommand):
    help = "Seed gamification badges"

    def handle(self, *args, **options):
        created = updated = 0
        for raw in BADGES:
            _, was_created = Badge.objects.update_or_create(
                slug=raw["slug"],
                defaults={
                    "name": raw["name"],
                    "description": raw["description"],
                    "icon": raw["icon"],
                    "points_required": raw["points_required"],
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Badges created={created} updated={updated}"))
