"""
Test suite for the v1 `/products` endpoint of the ChocoMax API.

This module uses the `v1_get` utility to avoid repeating the API version path.
"""

from fastapi.testclient import TestClient

from app.main import app
from tests.utils.request import v1_get

client = TestClient(app)


def test_products():
    """
    Test that the `/api/v1/products` endpoint returns a 200 status
    and responds with a JSON list.
    """
    response = v1_get(client, "/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
