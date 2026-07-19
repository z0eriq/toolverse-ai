from __future__ import annotations

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.engagement.models import Collection, ToolComment, ToolReview
from apps.engagement.serializers import (
    CollectionSerializer,
    ToolCommentSerializer,
    ToolReviewSerializer,
)
from apps.users.models import Profile


class CommunityProfileView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, username: str):
        try:
            profile = Profile.objects.select_related("user").get(
                public_username=username,
                is_public=True,
            )
        except Profile.DoesNotExist as exc:
            raise NotFound("Profile not found") from exc

        collections = Collection.objects.filter(
            user=profile.user,
            is_public=True,
        ).prefetch_related("items", "items__tool")

        return success_response(
            {
                "username": profile.public_username,
                "headline": profile.headline,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url,
                "name": profile.user.name,
                "collections": CollectionSerializer(collections, many=True).data,
            }
        )


class CommunityCollectionListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        qs = (
            Collection.objects.filter(is_public=True)
            .exclude(public_slug__isnull=True)
            .exclude(public_slug="")
            .select_related("user")
            .prefetch_related("items", "items__tool")
            .order_by("-updated_at")
        )
        return success_response(CollectionSerializer(qs[:100], many=True).data)


class CommunityCollectionDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, public_slug: str):
        try:
            collection = (
                Collection.objects.filter(is_public=True, public_slug=public_slug)
                .prefetch_related("items", "items__tool", "items__tool__category")
                .get()
            )
        except Collection.DoesNotExist as exc:
            raise NotFound("Collection not found") from exc
        return success_response(CollectionSerializer(collection).data)


class ModerationQueueView(APIView):
    """Pending ToolReview + ToolComment for admin moderation."""

    permission_classes = (IsAdminRole,)

    def get(self, request):
        reviews = (
            ToolReview.objects.filter(status=ToolReview.Status.PENDING)
            .select_related("user", "tool")
            .order_by("-created_at")[:100]
        )
        comments = (
            ToolComment.objects.filter(status=ToolComment.Status.PENDING)
            .select_related("user", "tool")
            .order_by("-created_at")[:100]
        )
        return success_response(
            {
                "reviews": ToolReviewSerializer(reviews, many=True).data,
                "comments": ToolCommentSerializer(comments, many=True).data,
            }
        )
