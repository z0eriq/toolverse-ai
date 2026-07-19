from django.urls import path

from apps.favorites.views import FavoriteDeleteView, FavoriteListCreateView

urlpatterns = [
    path("", FavoriteListCreateView.as_view(), name="favorites"),
    path("<str:tool_id>/", FavoriteDeleteView.as_view(), name="favorites-delete"),
]
