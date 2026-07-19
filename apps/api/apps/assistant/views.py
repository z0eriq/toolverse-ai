from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.assistant.models import AssistantSession
from apps.assistant.services import recommend_tools
from apps.common.exceptions import success_response


class AssistantThrottle(UserRateThrottle):
    scope = "assistant"


class AssistantAnonThrottle(AnonRateThrottle):
    scope = "assistant"


class AssistantChatView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AssistantThrottle, AssistantAnonThrottle)

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response(
                {"success": False, "error": {"message": "message is required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(message) > 2000:
            return Response(
                {"success": False, "error": {"message": "message too long (max 2000)"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = None
        session_id = request.data.get("session_id")
        if session_id:
            session = AssistantSession.objects.filter(pk=session_id).first()
        elif request.data.get("persist"):
            session = AssistantSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=str(request.data.get("session_key") or "")[:64],
            )

        locale = str(request.data.get("locale") or "en")[:10]
        result = recommend_tools(
            message,
            user=request.user if request.user.is_authenticated else None,
            session=session,
            locale=locale,
        )
        payload = {
            "reply": result["reply"],
            "recommended_tools": result["recommended_tools"],
            "meta": result.get("meta") or {},
        }
        if session is not None:
            payload["session_id"] = session.pk
        return success_response(payload)
