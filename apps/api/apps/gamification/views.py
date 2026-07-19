from __future__ import annotations

from rest_framework import permissions
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.gamification.models import Badge
from apps.gamification.services import get_user_gamification


class GamificationMeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return success_response(get_user_gamification(request.user))


class BadgeCatalogView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        qs = Badge.objects.filter(is_active=True).order_by("points_required", "slug")
        return success_response(
            [
                {
                    "slug": b.slug,
                    "name": b.name,
                    "description": b.description,
                    "icon": b.icon,
                    "points_required": b.points_required,
                }
                for b in qs
            ]
        )
