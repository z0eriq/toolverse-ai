from django.urls import path

from apps.creator_hub.views import (
    AdminCreatorRollupView,
    AdminCreatorSubmissionApproveView,
    AdminCreatorSubmissionListView,
    AdminCreatorSubmissionRejectView,
    CreatorPayoutsView,
    CreatorProfileView,
    CreatorSubmissionListCreateView,
    CreatorSubmissionSubmitView,
    CreatorUsageView,
)

urlpatterns = [
    path("profile/", CreatorProfileView.as_view(), name="creator-profile"),
    path("submissions/", CreatorSubmissionListCreateView.as_view(), name="creator-submissions"),
    path(
        "submissions/<int:pk>/submit/",
        CreatorSubmissionSubmitView.as_view(),
        name="creator-submission-submit",
    ),
    path("usage/", CreatorUsageView.as_view(), name="creator-usage"),
    path("payouts/", CreatorPayoutsView.as_view(), name="creator-payouts"),
]

admin_urlpatterns = [
    path(
        "submissions/",
        AdminCreatorSubmissionListView.as_view(),
        name="admin-creator-submissions",
    ),
    path(
        "submissions/<int:pk>/approve/",
        AdminCreatorSubmissionApproveView.as_view(),
        name="admin-creator-approve",
    ),
    path(
        "submissions/<int:pk>/reject/",
        AdminCreatorSubmissionRejectView.as_view(),
        name="admin-creator-reject",
    ),
    path("rollup/", AdminCreatorRollupView.as_view(), name="admin-creator-rollup"),
]
