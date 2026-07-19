from __future__ import annotations

from apps.monetization.models import AdPlacement

DEFAULT_PLACEMENTS: list[dict] = [
    {"key": AdPlacement.Key.BANNER, "enabled": True, "network": AdPlacement.Network.ADSENSE, "config": {"slot": "banner"}},
    {"key": AdPlacement.Key.IN_TOOL, "enabled": True, "network": AdPlacement.Network.ADSENSE, "config": {"slot": "in-tool"}},
    {"key": AdPlacement.Key.SIDEBAR, "enabled": True, "network": AdPlacement.Network.ADSENSE, "config": {"slot": "sidebar"}},
    {"key": AdPlacement.Key.SATELLITE, "enabled": True, "network": AdPlacement.Network.ADSENSE, "config": {"slot": "satellite"}},
]


def ensure_default_placements() -> int:
    created = 0
    for item in DEFAULT_PLACEMENTS:
        _, was_created = AdPlacement.objects.get_or_create(
            key=item["key"],
            defaults={
                "enabled": item["enabled"],
                "network": item["network"],
                "config": item["config"],
            },
        )
        if was_created:
            created += 1
    return created
