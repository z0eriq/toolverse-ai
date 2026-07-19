from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tools_registry.dynamic_views import (
    DynamicToolDetailView,
    DynamicToolListCreateView,
    DynamicToolPublishView,
    DynamicToolRunView,
)
from apps.tools_registry.views import CategoryViewSet, SitemapToolsView, ToolViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("tools", ToolViewSet, basename="tool")

urlpatterns = [
    path("sitemap/tools/", SitemapToolsView.as_view(), name="sitemap-tools"),
    path("dynamic/<slug:slug>/run/", DynamicToolRunView.as_view(), name="dynamic-run"),
    path("", include(router.urls)),
]

# Admin dynamic builder routes are under /api/v1/admin/
