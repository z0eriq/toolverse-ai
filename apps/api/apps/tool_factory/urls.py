from django.urls import path

from apps.tool_factory.views import (
    ToolSpecBuildView,
    ToolSpecDetailView,
    ToolSpecListCreateView,
    ToolSpecPublishView,
)

urlpatterns = [
    path("specs/", ToolSpecListCreateView.as_view(), name="tool-factory-specs"),
    path("specs/<int:pk>/", ToolSpecDetailView.as_view(), name="tool-factory-spec-detail"),
    path("specs/<int:pk>/build/", ToolSpecBuildView.as_view(), name="tool-factory-build"),
    path("specs/<int:pk>/publish/", ToolSpecPublishView.as_view(), name="tool-factory-publish"),
]
