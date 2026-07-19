from django.urls import path

from apps.keywords.views import KeywordOpportunityListView, KeywordOpportunityTopView

urlpatterns = [
    path("", KeywordOpportunityListView.as_view(), name="admin-keywords-list"),
    path("top/", KeywordOpportunityTopView.as_view(), name="admin-keywords-top"),
]
