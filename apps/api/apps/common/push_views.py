from __future__ import annotations

from django.conf import settings
from rest_framework import permissions, serializers, status
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.common.models import PushSubscription


class PushSubscribeSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=2048)
    keys = serializers.DictField(child=serializers.CharField(allow_blank=True), required=False)
    user_agent = serializers.CharField(required=False, allow_blank=True, max_length=512)


class PushSubscribeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = PushSubscribeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        sub, created = PushSubscription.objects.update_or_create(
            endpoint=data["endpoint"],
            defaults={
                "user": request.user,
                "keys": data.get("keys") or {},
                "user_agent": data.get("user_agent")
                or request.META.get("HTTP_USER_AGENT", "")[:512],
                "is_active": True,
            },
        )
        return success_response(
            {
                "id": sub.pk,
                "created": created,
                "endpoint": sub.endpoint,
            },
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class PushAdminTestPingView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request):
        """Stub test ping — records intent without requiring pywebpush."""
        user_id = request.data.get("user_id") or request.user.pk
        qs = PushSubscription.objects.filter(is_active=True, user_id=user_id)
        count = qs.count()
        return success_response(
            {
                "pinged": False,
                "stub": True,
                "message": "Web Push send is stubbed in v1; subscription count returned.",
                "subscription_count": count,
                "vapid_public_configured": bool(getattr(settings, "VAPID_PUBLIC_KEY", "")),
            }
        )
