from django.urls import path

from apps.tools_registry.mobile_views import MobileToolListView

urlpatterns = [
    path("tools/", MobileToolListView.as_view(), name="mobile-tools"),
]
