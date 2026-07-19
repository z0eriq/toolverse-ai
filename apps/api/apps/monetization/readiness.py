"""AdSense / monetization readiness helpers."""

from __future__ import annotations

from typing import Any

from django.conf import settings

from apps.monetization.models import AdPlacement
from apps.monetization.seed import ensure_default_placements


def adsense_readiness() -> dict[str, Any]:
    """
    Report whether AdSense can be served: client id env + seeded placements.
    """
    ensure_default_placements()
    client_id = (getattr(settings, "ADSENSE_CLIENT_ID", "") or "").strip()
    placements = list(
        AdPlacement.objects.filter(network=AdPlacement.Network.ADSENSE).values(
            "key", "enabled", "config"
        )
    )
    enabled_count = sum(1 for p in placements if p.get("enabled"))
    adsense_ready = bool(client_id) and enabled_count > 0
    return {
        "adsense_ready": adsense_ready,
        "client_id_configured": bool(client_id),
        "client_id_prefix": client_id[:12] + "…" if len(client_id) > 12 else client_id,
        "placements_total": len(placements),
        "placements_enabled": enabled_count,
        "placements": placements,
    }
