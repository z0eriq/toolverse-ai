from django.urls import path

from apps.content_factory.autopilot_views import AutopilotApproveView, AutopilotRunListCreateView

urlpatterns = [
    path("runs/", AutopilotRunListCreateView.as_view(), name="admin-autopilot-runs"),
    path(
        "runs/<int:pk>/approve/",
        AutopilotApproveView.as_view(),
        name="admin-autopilot-approve",
    ),
]
