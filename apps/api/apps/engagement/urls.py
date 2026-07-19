from django.urls import path

from apps.engagement.views import (
    CollectionDetailView,
    CollectionItemAddView,
    CollectionItemRemoveView,
    CollectionListCreateView,
    SavedOutputDetailView,
    SavedOutputListCreateView,
    ToolCommentListCreateView,
    ToolCommentModerateView,
    ToolReviewListCreateView,
    ToolReviewModerateView,
)

urlpatterns = [
    path("saved-outputs/", SavedOutputListCreateView.as_view(), name="engagement-saved-outputs"),
    path(
        "saved-outputs/<int:pk>/",
        SavedOutputDetailView.as_view(),
        name="engagement-saved-output-detail",
    ),
    path("collections/", CollectionListCreateView.as_view(), name="engagement-collections"),
    path(
        "collections/<slug:slug>/",
        CollectionDetailView.as_view(),
        name="engagement-collection-detail",
    ),
    path(
        "collections/<slug:slug>/items/",
        CollectionItemAddView.as_view(),
        name="engagement-collection-add-item",
    ),
    path(
        "collections/<slug:slug>/items/<str:tool_id>/",
        CollectionItemRemoveView.as_view(),
        name="engagement-collection-remove-item",
    ),
    path("reviews/", ToolReviewListCreateView.as_view(), name="engagement-reviews"),
    path(
        "reviews/<int:pk>/moderate/",
        ToolReviewModerateView.as_view(),
        name="engagement-review-moderate",
    ),
    path("comments/", ToolCommentListCreateView.as_view(), name="engagement-comments"),
    path(
        "comments/<int:pk>/moderate/",
        ToolCommentModerateView.as_view(),
        name="engagement-comment-moderate",
    ),
]
