from django.urls import path

from apps.engagement.community_views import ModerationQueueView

urlpatterns = [
    path("queue/", ModerationQueueView.as_view(), name="admin-moderation-queue"),
]
