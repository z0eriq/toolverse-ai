from django.urls import path

from apps.marketplace.views import (
    AdminInvoiceListView,
    AdminSalesLeadListView,
    ApiKeyListCreateView,
    ApiKeyRevokeView,
    ApiUsageSummaryView,
    DeveloperOrgListCreateView,
    MarketplaceAnalyticsView,
    SalesLeadCreateView,
    StripeMeterWebhookView,
)

urlpatterns = [
    path("keys/", ApiKeyListCreateView.as_view(), name="marketplace-keys"),
    path("keys/<int:pk>/revoke/", ApiKeyRevokeView.as_view(), name="marketplace-keys-revoke"),
    path("usage/", ApiUsageSummaryView.as_view(), name="marketplace-usage"),
    path("analytics/", MarketplaceAnalyticsView.as_view(), name="marketplace-analytics"),
    path("orgs/", DeveloperOrgListCreateView.as_view(), name="marketplace-orgs"),
    path("webhooks/stripe/", StripeMeterWebhookView.as_view(), name="marketplace-stripe-webhook"),
    path("leads/", SalesLeadCreateView.as_view(), name="marketplace-leads"),
]

admin_urlpatterns = [
    path("invoices/", AdminInvoiceListView.as_view(), name="admin-marketplace-invoices"),
    path("leads/", AdminSalesLeadListView.as_view(), name="admin-marketplace-leads"),
]
