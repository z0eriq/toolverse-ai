from django.urls import path

from apps.analytics.views import (
    CommandCenterView,
    DashboardView,
    FunnelView,
    GrowthDashboardView,
    TrackEventView,
)

urlpatterns = [
    path("track/", TrackEventView.as_view(), name="analytics-track"),
    path("dashboard/", DashboardView.as_view(), name="analytics-dashboard"),
    path("growth/", GrowthDashboardView.as_view(), name="analytics-growth"),
    path("funnels/", FunnelView.as_view(), name="analytics-funnels"),
]

# Mounted from api_urls under admin/command-center/
admin_urlpatterns = [
    path("", CommandCenterView.as_view(), name="admin-command-center"),
]
