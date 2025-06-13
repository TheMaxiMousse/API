"""
Test suite for the v1 `/orders` endpoint of the ChocoMax API.

This module uses the `v1_get` utility to avoid repeating the API version path.
"""

from fastapi.testclient import TestClient

from tests.utils.request import v1_get


def test_orders(client: TestClient):
    """
    Test that the `/api/v1/orders` endpoint returns a 200 status
    and responds with a JSON list.
    """
    response = v1_get(client, "/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
