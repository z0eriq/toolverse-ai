from django.urls import path

from apps.engagement.community_views import (
    CommunityCollectionDetailView,
    CommunityCollectionListView,
    CommunityProfileView,
)

urlpatterns = [
    path(
        "profiles/<slug:username>/",
        CommunityProfileView.as_view(),
        name="community-profile",
    ),
    path(
        "collections/",
        CommunityCollectionListView.as_view(),
        name="community-collections",
    ),
    path(
        "collections/<slug:public_slug>/",
        CommunityCollectionDetailView.as_view(),
        name="community-collection-detail",
    ),
]
