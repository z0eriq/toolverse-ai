from django.urls import path

from apps.gamification.views import BadgeCatalogView, GamificationMeView

urlpatterns = [
    path("me/", GamificationMeView.as_view(), name="gamification-me"),
    path("badges/", BadgeCatalogView.as_view(), name="gamification-badges"),
]
