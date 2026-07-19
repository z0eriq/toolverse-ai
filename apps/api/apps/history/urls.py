from django.urls import path

from apps.history.views import HistoryListCreateView

urlpatterns = [
    path("", HistoryListCreateView.as_view(), name="history"),
]
