import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Create a FastAPI test client for testing the application.

    Returns:
        TestClient: FastAPI test client instance.
    """
    client = TestClient(app)
    yield client
    client.close()
