from django.urls import path

from apps.ai_providers.views import AICompleteView, AIUsageSummaryView

urlpatterns = [
    path("complete/", AICompleteView.as_view(), name="ai-complete"),
    path("usage/", AIUsageSummaryView.as_view(), name="ai-usage"),
]
