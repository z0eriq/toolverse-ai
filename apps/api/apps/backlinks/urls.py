from django.urls import path

from apps.backlinks.views import (
    BacklinkCampaignListCreateView,
    BacklinkOpportunityListCreateView,
    BacklinkOpportunityStatusView,
    BacklinkTargetListCreateView,
)

urlpatterns = [
    path("targets/", BacklinkTargetListCreateView.as_view(), name="admin-backlink-targets"),
    path("campaigns/", BacklinkCampaignListCreateView.as_view(), name="admin-backlink-campaigns"),
    path(
        "opportunities/",
        BacklinkOpportunityListCreateView.as_view(),
        name="admin-backlink-opportunities",
    ),
    path(
        "opportunities/<int:pk>/status/",
        BacklinkOpportunityStatusView.as_view(),
        name="admin-backlink-opportunity-status",
    ),
]
