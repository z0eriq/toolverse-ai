from django.urls import path

from apps.programmatic_seo.views import (
    ProgrammaticPageByPathView,
    ProgrammaticPageListView,
    ProgrammaticSitemapView,
)

urlpatterns = [
    path("", ProgrammaticPageListView.as_view(), name="programmatic-list"),
    path("by-path/", ProgrammaticPageByPathView.as_view(), name="programmatic-by-path"),
    path("sitemap/", ProgrammaticSitemapView.as_view(), name="programmatic-sitemap"),
]
