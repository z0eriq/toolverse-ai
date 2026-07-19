"""Mobile-optimized public API endpoints."""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.tools_registry.models import Tool


class MobileClientThrottle(AnonRateThrottle):
    """Rate limit keyed by X-Client-Platform (mobile vs extension)."""

    scope = "mobile"

    def get_cache_key(self, request, view):
        platform = str(getattr(request, "client_platform", "") or "").lower()
        if not platform:
            platform = str(request.META.get("HTTP_X_CLIENT_PLATFORM") or "").lower()
        if platform in {"extension", "chrome", "firefox", "browser"}:
            self.scope = "extension"
        else:
            self.scope = "mobile"
        return super().get_cache_key(request, view)


class MobileToolListView(APIView):
    """Thin tool list for mobile clients (`?compact=1`)."""

    authentication_classes: list = []
    permission_classes = (AllowAny,)
    throttle_classes = (MobileClientThrottle,)

    def get(self, request):
        compact = str(request.query_params.get("compact") or "").lower() in {
            "1",
            "true",
            "yes",
        }
        qs = (
            Tool.objects.filter(is_active=True)
            .select_related("category")
            .order_by("order", "slug")
        )
        items = []
        for tool in qs[:500]:
            name = tool.name if isinstance(tool.name, dict) else {"en": str(tool.name or "")}
            row = {
                "slug": tool.slug,
                "category": tool.category.slug if tool.category_id else "",
                "name": {"en": str(name.get("en") or next(iter(name.values()), tool.slug))},
            }
            if not compact:
                row["tool_id"] = tool.tool_id
                row["icon"] = tool.icon
            items.append(row)
        return success_response(items)
