"""Stripe checkout session — real when STRIPE_SECRET_KEY set, else stub."""

from __future__ import annotations

from typing import Any

from django.conf import settings


def create_checkout_session(
    *,
    user,
    price_id: str = "",
    success_url: str = "",
    cancel_url: str = "",
) -> dict[str, Any]:
    """
    Create a Stripe Checkout Session when credentials exist.
    Otherwise return a stub payload so pricing CTAs stay wired in all envs.
    """
    secret = (getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    price = (price_id or getattr(settings, "STRIPE_PRICE_ID_PREMIUM", "") or "").strip()
    success = success_url or getattr(settings, "STRIPE_SUCCESS_URL", "")
    cancel = cancel_url or getattr(settings, "STRIPE_CANCEL_URL", "")

    if not secret:
        return {
            "url": "/pricing?checkout=stub",
            "status": "stub",
            "session_id": None,
            "message": "STRIPE_SECRET_KEY not configured — stub checkout returned",
        }

    try:
        import stripe  # type: ignore

        stripe.api_key = secret
        params: dict[str, Any] = {
            "mode": "subscription",
            "success_url": success,
            "cancel_url": cancel,
            "line_items": [{"price": price or "price_stub", "quantity": 1}],
        }
        if user and getattr(user, "email", None):
            params["customer_email"] = user.email
        if user and getattr(user, "id", None):
            params["client_reference_id"] = str(user.id)
            params["metadata"] = {"user_id": str(user.id)}

        session = stripe.checkout.Session.create(**params)
        return {
            "url": session.url,
            "status": "created",
            "session_id": session.id,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": "/pricing?checkout=error",
            "status": "error",
            "session_id": None,
            "message": str(exc)[:500],
        }
