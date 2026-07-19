from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.marketplace.billing import generate_invoices_from_usage
from apps.marketplace.models import ApiInvoiceStub, ApiKey, ApiUsage, DeveloperOrganization

User = get_user_model()


@pytest.mark.django_db
def test_invoice_stub_created_from_usage():
    user = User.objects.create_user(email="bill@example.com", password="pass12345")
    org = DeveloperOrganization.objects.create(name="Bill Org", owner=user)
    key, _ = ApiKey.create_for_user(user, name="prod")
    ApiUsage.objects.create(
        api_key=key,
        endpoint="/tools/",
        method="GET",
        status_code=200,
        units=25,
    )
    key.usage_this_month = 25
    key.save(update_fields=["usage_this_month", "updated_at"])

    result = generate_invoices_from_usage()
    assert result["created"] >= 1
    stub = ApiInvoiceStub.objects.get(org=org)
    assert stub.status == ApiInvoiceStub.Status.DRAFT
    assert stub.usage_units >= 25
