"""Seed example marketing campaigns (draft/active — never auto-spend)."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.campaigns.models import MarketingCampaign


EXAMPLES = [
    {
        "key": "launch-search-brand",
        "name": "Launch Search — Brand",
        "channel": MarketingCampaign.Channel.SEARCH,
        "status": MarketingCampaign.Status.ACTIVE,
        "budget_cents": 50_000,
        "meta": {"utm_campaign": "launch-search-brand", "notes": "Brand keywords"},
    },
    {
        "key": "newsletter-digest",
        "name": "Newsletter Digest",
        "channel": MarketingCampaign.Channel.EMAIL,
        "status": MarketingCampaign.Status.DRAFT,
        "budget_cents": 0,
        "meta": {"utm_campaign": "newsletter-digest"},
    },
]


class Command(BaseCommand):
    help = "Seed 1–2 example MarketingCampaign rows"

    def handle(self, *args, **options):
        created = 0
        now = timezone.now()
        for item in EXAMPLES:
            _, was_created = MarketingCampaign.objects.get_or_create(
                key=item["key"],
                defaults={
                    "name": item["name"],
                    "channel": item["channel"],
                    "status": item["status"],
                    "budget_cents": item["budget_cents"],
                    "starts_at": now if item["status"] == MarketingCampaign.Status.ACTIVE else None,
                    "meta": item["meta"],
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"seed_campaigns: created={created}"))
