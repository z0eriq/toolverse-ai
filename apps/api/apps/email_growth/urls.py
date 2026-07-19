from django.urls import path

from apps.email_growth.views import (
    AdminCampaignListCreateView,
    AdminCampaignSendTestView,
    NewsletterSubscribeView,
)

# Public newsletter routes (mounted at /api/v1/newsletter/)
urlpatterns = [
    path("subscribe/", NewsletterSubscribeView.as_view(), name="newsletter-subscribe"),
]

# Admin campaign routes (mounted at /api/v1/admin/email/)
admin_urlpatterns = [
    path("campaigns/", AdminCampaignListCreateView.as_view(), name="admin-email-campaigns"),
    path(
        "campaigns/<int:pk>/send-test/",
        AdminCampaignSendTestView.as_view(),
        name="admin-email-send-test",
    ),
]
