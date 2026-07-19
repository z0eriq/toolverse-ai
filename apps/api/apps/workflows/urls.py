from django.urls import path

from apps.workflows.views import (
    AdminWorkflowTemplateListView,
    WorkflowDetailView,
    WorkflowListCreateView,
    WorkflowRunView,
    WorkflowSharedView,
    WorkflowTemplateListView,
    WorkflowUsageView,
)

urlpatterns = [
    path("", WorkflowListCreateView.as_view(), name="workflows-list"),
    path("templates/", WorkflowTemplateListView.as_view(), name="workflows-templates"),
    path("usage/", WorkflowUsageView.as_view(), name="workflows-usage"),
    path("shared/<uuid:token>/", WorkflowSharedView.as_view(), name="workflows-shared"),
    path("<int:pk>/", WorkflowDetailView.as_view(), name="workflows-detail"),
    path("<int:pk>/run/", WorkflowRunView.as_view(), name="workflows-run"),
]

admin_urlpatterns = [
    path("templates/", AdminWorkflowTemplateListView.as_view(), name="admin-workflows-templates"),
]
