from django.urls import path

from apps.referrals.views import (
    AdminReferralStatsView,
    ReferralClaimView,
    ReferralMeView,
    ReferralRedirectInfoView,
)

urlpatterns = [
    path("me/", ReferralMeView.as_view(), name="referrals-me"),
    path("claim/", ReferralClaimView.as_view(), name="referrals-claim"),
    path("r/<slug:code>/", ReferralRedirectInfoView.as_view(), name="referrals-redirect"),
]

admin_urlpatterns = [
    path("stats/", AdminReferralStatsView.as_view(), name="admin-referrals-stats"),
]
