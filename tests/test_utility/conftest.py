import pytest


@pytest.fixture
def sample_email():
    """
    Fixture to provide a sample email for testing.
    This can be used in tests that require an email.
    """
    return "user@example.com"


@pytest.fixture
def sample_phone():
    """
    Fixture to provide a sample phone number for testing.
    This can be used in tests that require a phone number.
    """
    return "+1234567890"
