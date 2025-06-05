"""
Utility functions to simplify versioned API requests in tests.

These helpers reduce duplication of versioned API paths like `/api/v1/...`,
improving readability and consistency in test files.
"""

from fastapi.testclient import TestClient


def api_get(client: TestClient, version: str, path: str) -> TestClient:
    """
    Perform a GET request to a versioned API path.

    Args:
        client (TestClient): FastAPI test client.
        version (str): API version, e.g., 'v1' or 'v2'.
        path (str): Path to append after the version, e.g., '/orders'.

    Returns:
        Response: FastAPI test client response.
    """
    return client.get(f"/api/{version}{path}")


def v1_get(client: TestClient, path: str) -> TestClient:
    """
    Perform a GET request to a v1 API endpoint.

    Args:
        client (TestClient): FastAPI test client.
        path (str): Path to append after `/api/v1`.

    Returns:
        Response: FastAPI test client response.
    """
    return api_get(client, "v1", path)


def v2_get(client: TestClient, path: str) -> TestClient:
    """
    Perform a GET request to a v2 API endpoint.

    Args:
        client (TestClient): FastAPI test client.
        path (str): Path to append after `/api/v2`.

    Returns:
        Response: FastAPI test client response.
    """
    return api_get(client, "v2", path)
