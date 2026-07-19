from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.email_growth.models import EmailCampaign
from apps.email_growth.serializers import (
    EmailCampaignCreateSerializer,
    EmailCampaignSerializer,
    NewsletterSubscribeSerializer,
    NewsletterSubscriberSerializer,
    SendTestSerializer,
)
from apps.email_growth.services import send_campaign_test, subscribe_newsletter


class NewsletterSubscribeView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        ser = NewsletterSubscribeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sub = subscribe_newsletter(
            ser.validated_data["email"],
            locale=ser.validated_data.get("locale") or "en",
            source=ser.validated_data.get("source") or "web",
        )
        return success_response(
            NewsletterSubscriberSerializer(sub).data,
            status_code=status.HTTP_201_CREATED,
        )


class AdminCampaignListCreateView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        qs = EmailCampaign.objects.all().order_by("-created_at")[:100]
        return success_response(EmailCampaignSerializer(qs, many=True).data)

    def post(self, request):
        ser = EmailCampaignCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(created_by=request.user)
        return success_response(
            EmailCampaignSerializer(obj).data,
            status_code=status.HTTP_201_CREATED,
        )


class AdminCampaignSendTestView(APIView):
    permission_classes = (IsAdminRole,)

    def post(self, request, pk: int):
        try:
            campaign = EmailCampaign.objects.get(pk=pk)
        except EmailCampaign.DoesNotExist as exc:
            raise NotFound("Campaign not found") from exc
        ser = SendTestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        log = send_campaign_test(campaign, ser.validated_data["email"])
        return success_response(
            {
                "status": log.status,
                "email": log.email,
                "error": log.error,
                "meta": log.meta,
            }
        )
