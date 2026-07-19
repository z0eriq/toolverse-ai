from django.urls import path

from apps.launch_readiness.views import LaunchReadinessView

urlpatterns = [
    path("", LaunchReadinessView.as_view(), name="admin-launch-readiness"),
]
