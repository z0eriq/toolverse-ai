from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.views import APIView

from apps.analytics.models import AnalyticsEvent
from apps.blog.models import BlogPost
from apps.common.exceptions import success_response
from apps.history.models import ToolHistory
from apps.subscriptions.models import Subscription
from apps.tools_registry.models import Tool

User = get_user_model()


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_staff)
        )


class AdminMetricsView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        return success_response(
            {
                "users": User.objects.count(),
                "tools": Tool.objects.filter(is_active=True).count(),
                "premium_tools": Tool.objects.filter(is_active=True, premium=True).count(),
                "history_events": ToolHistory.objects.count(),
                "analytics_events": AnalyticsEvent.objects.count(),
                "blog_posts": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).count(),
                "premium_subscribers": Subscription.objects.filter(
                    status=Subscription.Status.ACTIVE, plan__slug="premium"
                ).count(),
                "top_tools": list(
                    Tool.objects.filter(is_active=True)
                    .order_by("-usage_count")
                    .values("tool_id", "slug", "usage_count")[:10]
                ),
            }
        )
