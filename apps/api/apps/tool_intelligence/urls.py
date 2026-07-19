from django.urls import path

from apps.tool_intelligence.views import (
    ToolOpportunityListView,
    ToolOpportunityQueueView,
    ToolPerformanceScoreListView,
)

urlpatterns = [
    path("", ToolOpportunityListView.as_view(), name="admin-tool-opportunities"),
    path(
        "<int:pk>/queue/",
        ToolOpportunityQueueView.as_view(),
        name="admin-tool-opportunity-queue",
    ),
]

tool_scores_urlpatterns = [
    path("", ToolPerformanceScoreListView.as_view(), name="admin-tool-scores"),
]
