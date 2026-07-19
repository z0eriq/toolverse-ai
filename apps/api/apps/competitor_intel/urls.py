from django.urls import path

from apps.competitor_intel.views import (
    CompetitorDomainDetailView,
    CompetitorDomainListCreateView,
    CompetitorOpportunityListView,
    CompetitorRecomputeView,
)

urlpatterns = [
    path("domains/", CompetitorDomainListCreateView.as_view(), name="admin-competitor-domains"),
    path(
        "domains/<int:pk>/",
        CompetitorDomainDetailView.as_view(),
        name="admin-competitor-domain-detail",
    ),
    path(
        "opportunities/",
        CompetitorOpportunityListView.as_view(),
        name="admin-competitor-opportunities",
    ),
    path("recompute/", CompetitorRecomputeView.as_view(), name="admin-competitor-recompute"),
]
