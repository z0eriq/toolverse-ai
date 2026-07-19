from django.urls import path

from apps.admin_api.views import AdminMetricsView
from apps.tools_registry.dynamic_views import (
    DynamicToolDetailView,
    DynamicToolListCreateView,
    DynamicToolPublishView,
)

urlpatterns = [
    path("metrics/", AdminMetricsView.as_view(), name="admin-metrics"),
    path("tools/dynamic/", DynamicToolListCreateView.as_view(), name="admin-dynamic-tools"),
    path(
        "tools/dynamic/<int:pk>/",
        DynamicToolDetailView.as_view(),
        name="admin-dynamic-tool-detail",
    ),
    path(
        "tools/dynamic/<int:pk>/publish/",
        DynamicToolPublishView.as_view(),
        name="admin-dynamic-tool-publish",
    ),
]
