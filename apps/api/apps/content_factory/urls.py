from django.urls import path

from apps.content_factory.views import (
    ContentItemDetailView,
    ContentItemListCreateView,
    ContentPublishView,
    ContentRegenerateView,
    PromptTemplateListCreateView,
)

urlpatterns = [
    path("templates/", PromptTemplateListCreateView.as_view(), name="content-templates"),
    path("", ContentItemListCreateView.as_view(), name="content-list"),
    path("<int:pk>/", ContentItemDetailView.as_view(), name="content-detail"),
    path("<int:pk>/publish/", ContentPublishView.as_view(), name="content-publish"),
    path("<int:pk>/regenerate/", ContentRegenerateView.as_view(), name="content-regenerate"),
]
