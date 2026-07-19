from django.urls import path

from apps.campaigns.views import (
    CampaignDetailView,
    CampaignListCreateView,
    CampaignResultListCreateView,
    CampaignSummaryView,
)

urlpatterns = [
    path("", CampaignListCreateView.as_view(), name="admin-campaigns"),
    path("summary/", CampaignSummaryView.as_view(), name="admin-campaigns-summary"),
    path("results/", CampaignResultListCreateView.as_view(), name="admin-campaign-results"),
    path("<int:pk>/", CampaignDetailView.as_view(), name="admin-campaign-detail"),
]
