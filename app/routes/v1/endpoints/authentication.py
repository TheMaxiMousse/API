import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.v1.schemas.user import UserLogin, UserRegister
from app.utility.database import get_db
from app.utility.security import hash_email, hash_password, verify_password
from app.utility.string_utils import sanitize_username

router = APIRouter()


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Endpoint for user login."""
    email_hash = hash_email(data.email)
    password = data.password

    # Verify password
    result = await db.execute(
        text("SELECT get_password_hash_by_email_hash(:email_hash)"),
        {"email_hash": email_hash},
    )
    password_hash = result.scalar()

    if not password_hash or not verify_password(password_hash, password):
        raise HTTPException(401, "Invalid credentials")

    # TODO: Handle 2FA verification here

    # Retrieve user information
    result = await db.execute(
        text("SELECT * FROM get_user_info_by_email_hash(:email_hash)"),
        {"email_hash": email_hash},
    )
    user_info = result.fetchone()

    # TODO: Handle user session creation or token generation here and avoid returning sensitive information
    return dict(user_info._mapping)


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Endpoint for user registration."""
    token = data.token
    username = sanitize_username(data.username)
    password_hash = hash_password(data.password)
    language_id = data.language_id

    if not token:
        raise HTTPException(400, "Token is required for registration")

    # Check if the token exists in pending_users
    result = await db.execute(
        text("SELECT 1 FROM pending_users WHERE verification_token = :token"),
        {"token": token},
    )
    if not result.scalar():
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
                :preferred_language_id
            )
            """
        ),
        {
            "token": token,
            "username": username,
            "discriminator": discriminator,
            "password_hash": password_hash,
            "preferred_language_id": language_id,
        },
    )
    await db.commit()
    return {
        "message": "User registered successfully",
        "username": username,
        "discriminator": discriminator,
    }
