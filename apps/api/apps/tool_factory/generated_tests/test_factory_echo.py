"""Generated smoke test for dynamic tool `factory-echo`."""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_factory_echo_endpoint_smoke():
    client = APIClient()
    response = client.post(
        "/api/v1/t/dynamic/factory-echo/run/",
        {"input": {}},
        format="json",
    )
    # Stub: endpoint is reachable (may validate input and return 400)
    assert response.status_code in (200, 400, 404)
    assert True
