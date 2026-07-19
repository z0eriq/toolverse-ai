from django.urls import path

from apps.subscriptions.views import CheckoutSessionView, MySubscriptionView, PlanListView

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plans"),
    path("me/", MySubscriptionView.as_view(), name="my-subscription"),
]

billing_urlpatterns = [
    path(
        "checkout-session/",
        CheckoutSessionView.as_view(),
        name="billing-checkout-session",
    ),
]
