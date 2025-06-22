import sys
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.routes.v1.endpoints import authentication as auth_module

AUTH_PATH = "app.routes.v1.endpoints.authentication"


@pytest.fixture
def client():
    """
    Returns a FastAPI TestClient with the authentication router included.
    """
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(auth_module.router, prefix="/v1/auth")
    return TestClient(app)


@pytest.fixture(autouse=True)
def patch_auth_dependencies():
    """
    Automatically patches authentication dependencies for all tests.
    Provides default mock return values for password hash, password verification,
    2FA secret, user info, and email hashing.
    """
    with (
        patch(
            f"{AUTH_PATH}.get_password_hash_by_email_hash", new_callable=AsyncMock
        ) as get_pw_hash_mock,
        patch(f"{AUTH_PATH}.verify_password") as verify_pw_mock,
        patch(
            f"{AUTH_PATH}.get_2fa_secret", new_callable=AsyncMock
        ) as get_2fa_secret_mock,
        patch(
            f"{AUTH_PATH}.get_user_info", new_callable=AsyncMock
        ) as get_user_info_mock,
        patch(f"{AUTH_PATH}.hash_email") as hash_email_mock,
    ):
        get_pw_hash_mock.return_value = "hashed-password"
        verify_pw_mock.return_value = True
        get_2fa_secret_mock.return_value = None
        get_user_info_mock.return_value = AsyncMock(_mapping={"username": "testuser"})
        hash_email_mock.return_value = "dummy-email-hash"
        yield {
            "get_pw_hash": get_pw_hash_mock,
            "verify_pw": verify_pw_mock,
            "get_2fa_secret": get_2fa_secret_mock,
            "get_user_info": get_user_info_mock,
            "hash_email": hash_email_mock,
        }


@pytest.fixture
def mock_db_and_override(client):
    """
    Provides a mock database session and overrides the get_db dependency.
    """
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    client.app.dependency_overrides[auth_module.get_db] = override_get_db
    return mock_db


@pytest.fixture
def login_payload():
    """Returns a function to generate login payloads."""

    def _payload(email="testuser", password="password123"):
        return {
            "email": email,
            "password": password,
        }

    return _payload


@pytest.fixture
def otp_payload():
    """Returns a function to generate OTP login payloads."""

    def _payload(token="validtoken", otp_code=123456):
        return {
            "token": token,
            "otp_code": otp_code,
        }

    return _payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password",
    [
        ("testuser", "password123"),
        ("admin", "adminpass"),
        ("user123", "userpass"),
        ("test.user", "testpass"),
        ("first.last", "flpass"),
    ],
)
async def test_login_returns_session_tokens(
    client,
    mock_db_and_override,
    patch_auth_dependencies,
    username,
    password,
    login_payload,
):
    """
    Test successful login returns opaque session and refresh tokens when 2FA is not required.
    """
    # Patch user info to include user_id for token generation simulation
    patch_auth_dependencies["get_user_info"].return_value = AsyncMock(
        _mapping={"username": "testuser"}
    )

    response = client.post("/v1/auth/login", json=login_payload())
    assert response.status_code == 200
    data = response.json()
    # Expect opaque tokens in response
    assert "session_token" in data
    assert "refresh_token" in data
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_2fa_required_returns_2fa_token(
    client, mock_db_and_override, patch_auth_dependencies, login_payload
):
    """
    Test login returns a 2FA-required response with a temporary token if 2FA is enabled.
    """

    # Simulate 2FA enabled
    class Dummy2FASecret:
        authentication_secret = "dummysecret"

    patch_auth_dependencies["get_2fa_secret"].return_value = Dummy2FASecret()

    # Simulate available 2FA methods
    with (
        patch(f"{AUTH_PATH}.text"),
        patch(f"{AUTH_PATH}.time"),
    ):
        # Patch DB call for 2FA methods
        mock_methods = [
            type("Row", (), {"authentication_method": "TOTP", "is_preferred": True})(),
            type("Row", (), {"authentication_method": "SMS", "is_preferred": False})(),
        ]
        mock_db = mock_db_and_override
        mock_execute = AsyncMock()
        mock_execute.fetchall.return_value = mock_methods
        mock_db.execute.return_value = mock_execute

        response = client.post("/v1/auth/login", json=login_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["2fa_required"] is True
    assert "token" in data
    assert set(data["methods"]) == {"TOTP", "SMS"}
    assert data["preferred_method"] == "TOTP"


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    client, mock_db_and_override, patch_auth_dependencies, login_payload
):
    """
    Test login with invalid credentials returns 401 and no tokens.
    """
    patch_auth_dependencies["verify_pw"].return_value = False

    response = client.post(
        "/v1/auth/login",
        json=login_payload(email="invaliduser", password="wrongpassword"),
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_missing_fields(client, mock_db_and_override):
    """
    Test login with missing fields returns 422 and no tokens.
    """
    response = client.post("/v1/auth/login", json={})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_otp_success_returns_tokens(
    client, mock_db_and_override, patch_auth_dependencies, otp_payload
):
    """
    Test /login/otp returns session and refresh tokens on successful OTP verification.
    """
    # Simulate valid 2FA session and OTP
    patch_auth_dependencies["get_2fa_secret"].return_value = AsyncMock(
        authentication_secret="dummysecret"
    )
    with patch(f"{AUTH_PATH}.verify_otp") as verify_otp_mock:
        verify_otp_mock.return_value = True
        patch_auth_dependencies["get_user_info"].return_value = AsyncMock(
            _mapping={"username": "testuser"}
        )
        # Simulate valid token in _2fa_sessions
        with patch.object(
            auth_module,
            "_2fa_sessions",
            {
                "validtoken": {
                    "email_hash": "dummy-email-hash",
                    "expires_at": 9999999999,
                }
            },
        ):
            response = client.post("/v1/auth/login/otp", json=otp_payload())

    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data
    assert "refresh_token" in data
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_otp_invalid_token(client, otp_payload):
    """
    Test /login/otp with an invalid or expired token returns 401.
    """
    with patch.object(auth_module, "_2fa_sessions", {}):
        response = client.post(
            "/v1/auth/login/otp", json=otp_payload(token="invalidtoken")
        )

    assert response.status_code == 401
    data = response.json()
    assert "2FA session token" in data["detail"]


@pytest.mark.asyncio
async def test_login_otp_invalid_otp(client, patch_auth_dependencies, otp_payload):
    """
    Test /login/otp with an invalid OTP code returns 401.
    """
    patch_auth_dependencies["get_2fa_secret"].return_value = AsyncMock(
        authentication_secret="dummysecret"
    )
    with patch(f"{AUTH_PATH}.verify_otp") as verify_otp_mock:
        verify_otp_mock.return_value = False
        with patch.object(
            auth_module,
            "_2fa_sessions",
            {
                "validtoken": {
                    "email_hash": "dummy-email-hash",
                    "expires_at": sys.maxsize,
                }
            },
        ):
            response = client.post("/v1/auth/login/otp", json=otp_payload())

    assert response.status_code == 401
    data = response.json()
    assert "Invalid 2FA code" in data["detail"]
