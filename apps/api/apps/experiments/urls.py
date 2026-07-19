from django.urls import path

from apps.experiments.views import (
    AdminExperimentListView,
    AdminExperimentResultsView,
    ExperimentAssignView,
    ExperimentTrackView,
)

urlpatterns = [
    path("assign/", ExperimentAssignView.as_view(), name="experiments-assign"),
    path("track/", ExperimentTrackView.as_view(), name="experiments-track"),
]

admin_urlpatterns = [
    path("", AdminExperimentListView.as_view(), name="admin-experiments-list"),
    path(
        "<int:pk>/results/",
        AdminExperimentResultsView.as_view(),
        name="admin-experiments-results",
    ),
]
