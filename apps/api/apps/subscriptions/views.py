from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.common.exceptions import success_response
from apps.subscriptions.checkout import create_checkout_session
from apps.subscriptions.models import Plan
from apps.subscriptions.serializers import PlanSerializer, SubscriptionSerializer
from apps.subscriptions.services import ensure_free_subscription, ensure_plans


class PlanListView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        ensure_plans()
        plans = Plan.objects.filter(is_active=True).order_by("price_cents")
        return success_response(PlanSerializer(plans, many=True).data)


class MySubscriptionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        sub = ensure_free_subscription(request.user)
        return success_response(SubscriptionSerializer(sub).data)


class CheckoutSessionView(APIView):
    """
    POST /api/v1/billing/checkout-session/
    Returns real Stripe session when STRIPE_SECRET_KEY is set, else {url, status: stub}.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        price_id = request.data.get("price_id") or ""
        success_url = request.data.get("success_url") or ""
        cancel_url = request.data.get("cancel_url") or ""
        user = request.user if request.user.is_authenticated else None
        result = create_checkout_session(
            user=user,
            price_id=str(price_id),
            success_url=str(success_url),
            cancel_url=str(cancel_url),
        )
        code = status.HTTP_200_OK
        if result.get("status") == "error":
            code = status.HTTP_502_BAD_GATEWAY
        return success_response(result, status_code=code)
