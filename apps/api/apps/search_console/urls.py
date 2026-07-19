from django.urls import path

from apps.search_console.views import (
    GSCOverviewView,
    GSCPagesView,
    GSCQueriesView,
    IndexedUrlListView,
)

urlpatterns = [
    path("overview/", GSCOverviewView.as_view(), name="admin-gsc-overview"),
    path("queries/", GSCQueriesView.as_view(), name="admin-gsc-queries"),
    path("pages/", GSCPagesView.as_view(), name="admin-gsc-pages"),
    path("indexed-urls/", IndexedUrlListView.as_view(), name="admin-gsc-indexed-urls"),
]
