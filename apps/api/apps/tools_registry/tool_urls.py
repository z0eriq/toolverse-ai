"""Dynamically mount per-tool API routes without hard-coding tool names."""

from __future__ import annotations

from django.urls import path
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.tools_registry.discovery import load_tool_plugins
from apps.tools_registry.dynamic_views import DynamicToolRunView

_plugins = load_tool_plugins()


class ToolApiThrottle(AnonRateThrottle):
    scope = "tool"


urlpatterns = [
    path("dynamic/<slug:slug>/run/", DynamicToolRunView.as_view(), name="tool-dynamic-run"),
]

for tool_id, plugin in _plugins.items():
    get_urls = getattr(plugin, "get_urls", None)
    if callable(get_urls):
        for pattern in get_urls():
            urlpatterns.append(pattern)
    else:

        @api_view(["GET"])
        @permission_classes([AllowAny])
        @throttle_classes([ToolApiThrottle])
        def _ping(request, _tool_id=tool_id):
            return Response({"success": True, "data": {"tool": _tool_id, "status": "ok"}})

        urlpatterns.append(path(f"{tool_id}/", _ping, name=f"tool-{tool_id}-ping"))
