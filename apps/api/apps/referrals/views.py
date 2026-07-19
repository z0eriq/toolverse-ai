from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.admin_api.views import IsAdminRole
from apps.common.exceptions import success_response
from apps.referrals.models import ReferralAttribution, ReferralCode
from apps.referrals.services import (
    attribute_signup,
    get_or_create_code,
    qualify_referral,
    referral_stats,
    track_click,
)


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ReferralMeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        code = get_or_create_code(request.user)
        made = ReferralAttribution.objects.filter(referrer=request.user).count()
        qualified = ReferralAttribution.objects.filter(
            referrer=request.user,
            status__in=("qualified", "rewarded"),
        ).count()
        return success_response(
            {
                "code": code.code,
                "is_active": code.is_active,
                "referrals_made": made,
                "qualified": qualified,
                "share_path": f"/r/{code.code}",
            }
        )

    def post(self, request):
        code = get_or_create_code(request.user)
        return success_response(
            {"code": code.code, "share_path": f"/r/{code.code}"},
            status_code=status.HTTP_201_CREATED,
        )


class ReferralClaimView(APIView):
    """Claim a referral code for the authenticated user (attribute signup)."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        code = (request.data.get("code") or "").strip()
        if not code:
            raise ValidationError({"code": "Required"})
        attr = attribute_signup(
            request.user,
            code,
            ip=_client_ip(request),
            device_hash=str(request.data.get("device_hash") or "")[:64],
        )
        if attr is None:
            raise ValidationError({"code": "Invalid referral code"})
        if attr.status == ReferralAttribution.Status.BLOCKED:
            raise ValidationError({"code": "Referral blocked (self-referral or abuse)"})
        # Auto-qualify on claim for v1 (email verified / first tool can refine later)
        qualify_referral(request.user)
        attr.refresh_from_db()
        return success_response(
            {
                "status": attr.status,
                "referrer_id": attr.referrer_id,
            }
        )


class ReferralRedirectInfoView(APIView):
    """Public redirect info JSON for /r/<code>/ landing."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AnonRateThrottle,)

    def get(self, request, code: str):
        ref = track_click(code, ip=_client_ip(request), meta={"ua": request.META.get("HTTP_USER_AGENT", "")[:200]})
        if not ref:
            raise ValidationError({"code": "Invalid referral code"})
        return success_response(
            {
                "code": ref.code,
                "cookie": "tv_ref",
                "ttl_days": 30,
                "redirect": "/",
            }
        )


class AdminReferralStatsView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        return success_response(referral_stats())
