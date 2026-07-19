from django.urls import path

from apps.common.push_views import PushAdminTestPingView, PushSubscribeView

urlpatterns = [
    path("subscribe/", PushSubscribeView.as_view(), name="push-subscribe"),
]

admin_urlpatterns = [
    path("test-ping/", PushAdminTestPingView.as_view(), name="admin-push-test-ping"),
]
