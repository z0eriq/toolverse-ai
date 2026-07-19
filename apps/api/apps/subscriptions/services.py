from apps.subscriptions.models import Plan, Subscription


def ensure_plans() -> None:
    free, _ = Plan.objects.get_or_create(
        slug="free",
        defaults={
            "name": "Free",
            "description": "Access to free tools with monthly run limits",
            "price_cents": 0,
            "features": ["Free tools", "Favorites", "History (30 days)", "50 tool runs / month"],
            "monthly_tool_runs": 50,
            "api_monthly_quota": 1000,
            "ads_free": False,
            "history_days": 30,
        },
    )
    # Keep free plan limits aligned for existing installs
    Plan.objects.filter(pk=free.pk).update(
        monthly_tool_runs=50,
        api_monthly_quota=1000,
        ads_free=False,
        history_days=30,
    )

    premium, created = Plan.objects.get_or_create(
        slug="premium",
        defaults={
            "name": "Pro",
            "description": "Unlimited tool runs, higher API quota, ad-free",
            "price_cents": 900,
            "features": [
                "All Premium tools",
                "Unlimited tool runs",
                "Ad-free experience",
                "Priority API rate limits",
                "Early access to AI tools",
            ],
            "monthly_tool_runs": -1,
            "api_monthly_quota": 100_000,
            "ads_free": True,
            "history_days": 365,
        },
    )
    updates = {
        "name": "Pro",
        "monthly_tool_runs": -1,
        "api_monthly_quota": 100_000,
        "ads_free": True,
        "history_days": 365,
    }
    if not created:
        Plan.objects.filter(pk=premium.pk).update(**updates)
    else:
        # defaults already applied; ensure name Pro
        Plan.objects.filter(pk=premium.pk).update(name="Pro")


def ensure_free_subscription(user) -> Subscription:
    ensure_plans()
    plan = Plan.objects.get(slug="free")
    sub, _ = Subscription.objects.get_or_create(
        user=user,
        defaults={"plan": plan, "status": Subscription.Status.ACTIVE},
    )
    return sub


def user_has_premium(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    sub = getattr(user, "subscription", None)
    if sub is None:
        return False
    return sub.is_active and sub.plan.slug == "premium"
