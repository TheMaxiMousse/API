"""
Test the home endpoint of the API.
"""


def test_home(client):
    """Test the home endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ChocoMax Shop API!"}
