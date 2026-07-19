from django.urls import path

from apps.monetization.views import (
    AdSenseReadyView,
    AdminAdPlacementDetailView,
    AdminAdPlacementListCreateView,
    AdminAdPerformanceListView,
    AdminAdRecommendationAcceptView,
    AdminAdRecommendationDismissView,
    AdminAdRecommendationListView,
    AdminAffiliateDetailView,
    AdminAffiliateListCreateView,
    AdminRevenueEventListCreateView,
    AdminRevenueSummaryView,
    AdminSponsoredDetailView,
    AdminSponsoredListCreateView,
    PublicAffiliatesView,
    PublicPlacementsView,
    PublicSponsoredView,
)

urlpatterns = [
    path("placements/", PublicPlacementsView.as_view(), name="monetization-placements"),
    path("affiliates/", PublicAffiliatesView.as_view(), name="monetization-affiliates"),
    path("sponsored/", PublicSponsoredView.as_view(), name="monetization-sponsored"),
    path("adsense-ready/", AdSenseReadyView.as_view(), name="monetization-adsense-ready"),
]

admin_urlpatterns = [
    path("placements/", AdminAdPlacementListCreateView.as_view(), name="admin-ad-placements"),
    path(
        "placements/<int:pk>/",
        AdminAdPlacementDetailView.as_view(),
        name="admin-ad-placement-detail",
    ),
    path("sponsored/", AdminSponsoredListCreateView.as_view(), name="admin-sponsored"),
    path("sponsored/<int:pk>/", AdminSponsoredDetailView.as_view(), name="admin-sponsored-detail"),
    path("affiliates/", AdminAffiliateListCreateView.as_view(), name="admin-affiliates"),
    path("affiliates/<int:pk>/", AdminAffiliateDetailView.as_view(), name="admin-affiliate-detail"),
    path("events/", AdminRevenueEventListCreateView.as_view(), name="admin-revenue-events"),
    path("summary/", AdminRevenueSummaryView.as_view(), name="admin-revenue-summary"),
    path("ad-performance/", AdminAdPerformanceListView.as_view(), name="admin-ad-performance"),
    path(
        "ad-recommendations/",
        AdminAdRecommendationListView.as_view(),
        name="admin-ad-recommendations",
    ),
    path(
        "ad-recommendations/<int:pk>/accept/",
        AdminAdRecommendationAcceptView.as_view(),
        name="admin-ad-recommendation-accept",
    ),
    path(
        "ad-recommendations/<int:pk>/dismiss/",
        AdminAdRecommendationDismissView.as_view(),
        name="admin-ad-recommendation-dismiss",
    ),
]
