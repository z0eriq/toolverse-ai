"""Seed starter competitor domains and keyword gaps."""

from django.core.management.base import BaseCommand

from apps.competitor_intel.models import CompetitorDomain, CompetitorKeyword
from apps.competitor_intel.services import recompute_competitor_opportunities

SEED = [
    {
        "domain": "ilovepdf.com",
        "name": "iLovePDF",
        "keywords": [
            ("merge pdf online", 2.0, 12000),
            ("compress pdf free", 3.0, 9000),
            ("split pdf online", 4.0, 7000),
        ],
    },
    {
        "domain": "smallpdf.com",
        "name": "Smallpdf",
        "keywords": [
            ("pdf to word", 1.0, 15000),
            ("edit pdf online", 5.0, 8000),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed competitor domains/keywords and recompute opportunities"

    def handle(self, *args, **options):
        for item in SEED:
            domain, _ = CompetitorDomain.objects.update_or_create(
                domain=item["domain"],
                defaults={"name": item["name"], "is_active": True},
            )
            for keyword, position, volume in item["keywords"]:
                CompetitorKeyword.objects.update_or_create(
                    competitor=domain,
                    keyword=keyword,
                    defaults={
                        "position": position,
                        "search_volume": volume,
                        "our_has_coverage": False,
                    },
                )
        result = recompute_competitor_opportunities()
        self.stdout.write(self.style.SUCCESS(f"Seeded competitors; {result}"))
