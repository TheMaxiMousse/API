"""
Authentication endpoints and utilities for user login, registration, and 2FA.

This module provides FastAPI endpoints for user authentication, including login,
two-factor authentication (2FA), and registration. It also includes utility
functions for interacting with the database and handling authentication logic.
"""

import json
import random
import secrets
import time
from urllib import request

from fastapi import APIRouter, Depends, HTTPException, Request
from pyotp import random_base32 as generate_otp_secret
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent

from app.routes.v1.schemas.user.login import UserLogin, UserLogin2FA
from app.routes.v1.schemas.user.register import UserRegister
from app.utility.database import get_db
from app.utility.security import hash_email, hash_password, verify_otp, verify_password
from app.utility.string_utils import sanitize_username

router = APIRouter()
_2fa_sessions = (
    {}
)  # Temporary in-memory store for 2FA sessions TODO: (replace with Redis or DB in production)


# --- Common utility functions ---


async def get_password_hash_by_email_hash(
    db: AsyncSession, email_hash: str
) -> str | None:
    """
    Retrieve the password hash for a user by their email hash.

    Args:
        db (AsyncSession): The database session.
        email_hash (str): The hashed email address.

    Returns:
        str | None: The password hash if found, otherwise None.
    """
    result = await db.execute(
        text("SELECT get_password_hash_by_email_hash(:email_hash)"),
        {"email_hash": email_hash},
    )
    return result.scalar()


async def get_2fa_secret(db: AsyncSession, email_hash: str, method: str = "TOTP"):
    """
    Retrieve the 2FA secret for a user by their email hash and authentication method.

    Args:
        db (AsyncSession): The database session.
        email_hash (str): The hashed email address.
        method (str): The authentication method (default: "TOTP").

    Returns:
        Row or None: The database row containing the 2FA secret, or None if not found.
    """
    result = await db.execute(
        text(
            "SELECT * FROM get_user_2fa_secret_by_email_hash(:email_hash, :auth_method)"
        ),
        {"email_hash": email_hash, "auth_method": method},
    )
    return result.fetchone()


async def get_user_info(db: AsyncSession, email_hash: str):
    """
    Retrieve user information by their email hash.

    Args:
        db (AsyncSession): The database session.
        email_hash (str): The hashed email address.

    Returns:
        Row or None: The database row containing user information, or None if not found.
    """
    result = await db.execute(
        text("SELECT * FROM get_user_info_by_email_hash(:email_hash)"),
        {"email_hash": email_hash},
    )
    return result.fetchone()


async def save_session_token(
    db: AsyncSession,
    user_id: int,
    session_token: str,
    device_info: str,
    ip_address: str,
):
    """
    Save a session token for a user with device and IP info.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The user's ID.
        session_token (str): The session token to save.
        device_info (str): Information about the user's device.
        ip_address (str): The user's IP address.
    """
    await db.execute(
        text(
            """
            CALL create_user_session_token(
                :p_user_id,
                :p_session_token,
                :p_device_info,
                :p_ip_address
            )
            """
        ),
        {
            "p_user_id": user_id,
            "p_session_token": session_token,
            "p_device_info": device_info,
            "p_ip_address": ip_address,
        },
    )
    await db.commit()


async def save_refresh_token(
    db: AsyncSession,
    user_id: int,
    session_token: str,
    device_info: str,
    ip_address: str,
):
    """
    Save a session token for a user with device and IP info.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The user's ID.
        session_token (str): The session token to save.
        device_info (str): Information about the user's device.
        ip_address (str): The user's IP address.
    """
    await db.execute(
        text(
            """
            CALL create_user_refresh_token(
                :p_user_id,
                :p_session_token,
                :p_device_info,
                :p_ip_address
            )
            """
        ),
        {
            "p_user_id": user_id,
            "p_session_token": session_token,
            "p_device_info": device_info,
            "p_ip_address": ip_address,
        },
    )
    await db.commit()


async def delete_refresh_token():
    """Delete a refresh token for a user"""
    # TODO


async def delete_access_token():
    """Delete an access token for a user"""
    # TODO


# --- Endpoints ---


@router.post("/login")
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Verify email and password, check if 2FA is required.

    Args:
        data (UserLogin): The login request payload.
        db (AsyncSession): The database session.

    Returns:
        dict: If 2FA is required, returns a dict with 2FA info and a temporary token.
              Otherwise, returns user info/session.
    Raises:
        HTTPException: If credentials are invalid.
    """
    email_hash = hash_email(data.email)
    password = data.password

    # Parse user agent for device info
    client_ip = request.client.host
    forwarded_ip = request.headers.get("X-Forwarded-For")
    ip_address = request.headers.get("X-Real-IP") or request.client.host
    user_agent_str = request.headers.get("User-Agent", "")
    user_agent = parse_user_agent(user_agent_str)

    device_info = json.dumps(
        {
            "os": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "browser": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "device": user_agent.device.family,
            "is_mobile": user_agent.is_mobile,
            "is_tablet": user_agent.is_tablet,
            "is_pc": user_agent.is_pc,
            "is_bot": user_agent.is_bot,
        }
    )

    # Verify password
    password_hash = await get_password_hash_by_email_hash(db, email_hash)
    if not password_hash or not verify_password(password, password_hash):
        raise HTTPException(401, "Invalid credentials")

    # Check if 2FA is enabled before fetching user info
    row = await get_2fa_secret(db, email_hash)
    user_2fa_secret = row.authentication_secret if row else None

    if user_2fa_secret:
        temp_token = secrets.token_urlsafe(32)

        # Store mapping with expiry (5 minutes)
        _2fa_sessions[temp_token] = {
            "email_hash": email_hash,
            "expires_at": time.time() + 300,
        }

        result = await db.execute(
            text("SELECT * FROM get_user_2fa_methods_by_email_hash(:email_hash)"),
            {"email_hash": email_hash},
        )
        methods_rows = await result.fetchall()
        methods = [row.authentication_method for row in methods_rows]
        preferred_method = next(
            (row.authentication_method for row in methods_rows if row.is_preferred),
            None,
        )

        if methods:
            return {
                "2fa_required": True,
                "token": temp_token,  # Return token instead of email_hash
                "methods": methods,
                "preferred_method": preferred_method,
            }

    user_info = await get_user_info(db, email_hash)

    session_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)

    await save_session_token(
        db,
        user_info.user_id,
        session_token,
        device_info,
        ip_address,
    )
    await save_refresh_token(
        db,
        user_info.user_id,
        refresh_token,
        device_info,
        ip_address,
    )

    return {
        **dict(user_info._mapping),
        "session_token": session_token,
        "refresh_token": refresh_token,
    }


@router.post("/login/otp")
async def login_otp(data: UserLogin2FA, db: AsyncSession = Depends(get_db)):
    """
    Step 2: Verify OTP code and return user info/session.

    Args:
        data (UserLogin2FA): The 2FA login request payload.
        db (AsyncSession): The database session.

    Returns:
        dict: User info/session if OTP is valid.
    Raises:
        HTTPException: If the session token is invalid/expired, 2FA is not enabled, or OTP is invalid.
    """
    # Validate the temporary session token
    session = _2fa_sessions.get(data.token)

    if not session or session["expires_at"] < time.time():
        raise HTTPException(401, "Invalid or expired 2FA session token")

    email_hash = session["email_hash"]

    # Get 2FA secret and method
    row = await get_2fa_secret(db, email_hash)
    secret = row.authentication_secret if row else None

    if not secret:
        raise HTTPException(400, "2FA is not enabled for this user")

    if not verify_otp(secret, data.otp_code):
        raise HTTPException(401, "Invalid 2FA code")

    user_info = await get_user_info(db, email_hash)

    session_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    await save_session_token(
        db,
        user_info.user_id,
        session_token,
        data.device_info,
        data.ip_address,
    )
    await save_refresh_token(
        db,
        user_info.user_id,
        refresh_token,
        data.device_info,
        data.ip_address,
    )
    return {
        **dict(user_info._mapping),
        "session_token": session_token,
        "refresh_token": refresh_token,
    }


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user registration.

    Args:
        data (UserRegister): The registration request payload.
        db (AsyncSession): The database session.

    Returns:
        dict: Registration result with username and discriminator.
    Raises:
        HTTPException: If the token is missing/invalid, all discriminators are taken, or email exists.
    """
    token = data.token
    username = sanitize_username(data.username)
    password_hash = hash_password(data.password)
    language_id = data.language_id
    otp_secret = generate_otp_secret()

    if not token:
        raise HTTPException(400, "Token is required for registration")

    # Check if the token exists and is valid using the new function
    result = await db.execute(
        text("SELECT is_verification_token_valid(:token)"),
        {"token": token},
    )
    is_valid = result.scalar()

    if not is_valid:
        raise HTTPException(400, "Invalid or expired verification token")

    # Retrieve the list of discriminators for the username
    result = await db.execute(
        text("SELECT get_used_discriminators(:username) AS discriminator"),
        {"username": username},
    )
    used_discriminators = [row.discriminator for row in result.fetchall()]
    available_discriminators = set(range(0, 10000)) - set(used_discriminators)

    if not available_discriminators:
        raise HTTPException(409, "All discriminators taken for this username")

    # Choose a random discriminator from the available ones
    discriminator = random.choice(list(available_discriminators))

    # Check if email is available
    result = await db.execute(
        text("SELECT is_email_available(:token) AS available"), {"token": token}
    )
    available = result.scalar()

    if not available:
        raise HTTPException(409, "Email already exists")

    await db.execute(
        text(
            """
            CALL register_user(
                :token,
                :username,
                :discriminator,
                :password_hash,
                :preferred_language_id,
                :otp_secret
            )
            """
        ),
        {
            "token": token,
            "username": username,
            "discriminator": discriminator,
            "password_hash": password_hash,
            "preferred_language_id": language_id,
            "otp_secret": otp_secret,
        },
    )
    await db.commit()
    return {
        "message": "User registered successfully",
        "username": username,
        "discriminator": discriminator,
    }
