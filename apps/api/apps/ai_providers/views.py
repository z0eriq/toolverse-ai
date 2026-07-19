from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.ai_providers.base import AIProviderError
from apps.ai_providers.models import AIUsageLog
from apps.ai_providers.router import get_ai_router
from apps.common.exceptions import success_response
from django.db.models import Count, Sum


class AIThrottle(UserRateThrottle):
    scope = "ai"


class AICompleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = (AIThrottle,)

    def post(self, request):
        from apps.common.limits import ToolRunLimitExceeded, check_tool_run_limit, increment_tool_run

        try:
            check_tool_run_limit(request.user)
        except ToolRunLimitExceeded as exc:
            return Response(
                {
                    "success": False,
                    "error": {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": exc.detail,
                    },
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        messages = request.data.get("messages")
        if not isinstance(messages, list) or not messages:
            return Response(
                {"success": False, "error": {"message": "messages array required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = get_ai_router().complete(
                messages,
                provider=request.data.get("provider"),
                model=request.data.get("model"),
                temperature=float(request.data.get("temperature", 0.2)),
                max_tokens=int(request.data.get("max_tokens", 1024)),
                user=request.user,
                tool_id=str(request.data.get("tool_id") or ""),
            )
        except AIProviderError as exc:
            return Response(
                {"success": False, "error": {"message": str(exc)}},
                status=exc.status_code or status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        increment_tool_run(request.user)
        return success_response(
            {
                "content": result.content,
                "provider": result.provider,
                "model": result.model,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
            }
        )


class AIUsageSummaryView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = AIUsageLog.objects.all()
        by_provider = list(
            qs.values("provider").annotate(
                calls=Count("id"),
                tokens_in=Sum("tokens_in"),
                tokens_out=Sum("tokens_out"),
                cost=Sum("cost_estimate"),
            )
        )
        return success_response({"total_calls": qs.count(), "by_provider": by_provider})
