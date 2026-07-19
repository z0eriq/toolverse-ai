from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.common.exceptions import success_response
from apps.subscriptions.services import ensure_free_subscription
from apps.users.serializers import (
    EmailTokenObtainPairSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthBurstThrottle(AnonRateThrottle):
    scope = "auth"


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AuthBurstThrottle,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        ensure_free_subscription(user)
        refresh = RefreshToken.for_user(user)
        return success_response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = (AuthBurstThrottle,)


class RefreshView(TokenRefreshView):
    throttle_classes = (AuthBurstThrottle,)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"success": False, "error": {"message": "refresh token required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:  # noqa: BLE001
            return Response(
                {"success": False, "error": {"message": "invalid refresh token"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return success_response({"detail": "logged out"})


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        return success_response(UserSerializer(request.user).data)

    def update(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "name" in request.data:
            request.user.name = request.data["name"]
            request.user.save(update_fields=["name", "updated_at"])
        return success_response(UserSerializer(request.user).data)
