from django.urls import path

from apps.jobs.views import JobCreateView, JobDetailView

urlpatterns = [
    path("", JobCreateView.as_view(), name="jobs-create"),
    path("<uuid:job_id>/", JobDetailView.as_view(), name="jobs-detail"),
]
