from django.urls import path

from apps.growth_agent.views import (
    GrowthActionApproveView,
    GrowthActionListView,
    GrowthActionRejectView,
    GrowthAgentRunListCreateView,
    GrowthInsightAcceptView,
    GrowthInsightDismissView,
    GrowthInsightListView,
    GrowthTaskAcceptView,
    GrowthTaskCompleteView,
    GrowthTaskListView,
)

urlpatterns = [
    path("runs/", GrowthAgentRunListCreateView.as_view(), name="admin-growth-agent-runs"),
    path("insights/", GrowthInsightListView.as_view(), name="admin-growth-agent-insights"),
    path(
        "insights/<int:pk>/accept/",
        GrowthInsightAcceptView.as_view(),
        name="admin-growth-agent-accept",
    ),
    path(
        "insights/<int:pk>/dismiss/",
        GrowthInsightDismissView.as_view(),
        name="admin-growth-agent-dismiss",
    ),
    path("tasks/", GrowthTaskListView.as_view(), name="admin-growth-agent-tasks"),
    path(
        "tasks/<int:pk>/accept/",
        GrowthTaskAcceptView.as_view(),
        name="admin-growth-agent-task-accept",
    ),
    path(
        "tasks/<int:pk>/complete/",
        GrowthTaskCompleteView.as_view(),
        name="admin-growth-agent-task-complete",
    ),
    path("actions/", GrowthActionListView.as_view(), name="admin-growth-agent-actions"),
    path(
        "actions/<int:pk>/approve/",
        GrowthActionApproveView.as_view(),
        name="admin-growth-agent-action-approve",
    ),
    path(
        "actions/<int:pk>/reject/",
        GrowthActionRejectView.as_view(),
        name="admin-growth-agent-action-reject",
    ),
]
