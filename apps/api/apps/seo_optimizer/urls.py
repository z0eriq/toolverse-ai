from django.urls import path

from apps.seo_optimizer.views import (
    SeoAnalyzeView,
    SeoAutopilotScanView,
    SeoHealthListCreateView,
    SeoHealthRecomputeView,
    SeoOpportunityTaskDetailView,
    SeoOpportunityTaskGenerateView,
    SeoOpportunityTaskListView,
    SeoPageIssueApplyView,
    SeoPageIssueDismissView,
    SeoPageIssueListView,
    SeoRecommendationAcceptView,
    SeoRecommendationDismissView,
    SeoRecommendationListView,
)

urlpatterns = [
    path("analyze/", SeoAnalyzeView.as_view(), name="admin-seo-analyze"),
    path("recommendations/", SeoRecommendationListView.as_view(), name="admin-seo-recommendations"),
    path(
        "recommendations/<int:pk>/accept/",
        SeoRecommendationAcceptView.as_view(),
        name="admin-seo-accept",
    ),
    path(
        "recommendations/<int:pk>/dismiss/",
        SeoRecommendationDismissView.as_view(),
        name="admin-seo-dismiss",
    ),
    path("health/", SeoHealthListCreateView.as_view(), name="admin-seo-health"),
    path("health/recompute/", SeoHealthRecomputeView.as_view(), name="admin-seo-health-recompute"),
    path(
        "opportunity-tasks/generate/",
        SeoOpportunityTaskGenerateView.as_view(),
        name="admin-seo-opportunity-tasks-generate",
    ),
    path(
        "opportunity-tasks/",
        SeoOpportunityTaskListView.as_view(),
        name="admin-seo-opportunity-tasks",
    ),
    path(
        "opportunity-tasks/<int:pk>/",
        SeoOpportunityTaskDetailView.as_view(),
        name="admin-seo-opportunity-task-detail",
    ),
    path("autopilot/scan/", SeoAutopilotScanView.as_view(), name="admin-seo-autopilot-scan"),
    path("issues/", SeoPageIssueListView.as_view(), name="admin-seo-issues"),
    path(
        "issues/<int:pk>/apply/",
        SeoPageIssueApplyView.as_view(),
        name="admin-seo-issue-apply",
    ),
    path(
        "issues/<int:pk>/dismiss/",
        SeoPageIssueDismissView.as_view(),
        name="admin-seo-issue-dismiss",
    ),
]
