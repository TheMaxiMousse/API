from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.v1.schemas.user.register import UserRegister
from app.utility.database import get_db
from app.utility.security import (
    encrypt_email,
    encrypt_phone,
    hash_email,
    hash_password,
    hash_phone,
)
from app.utility.string_utils import sanitize_username

router = APIRouter()


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Endpoint for user registration."""
    username = sanitize_username(data.username)
    email_encrypted = encrypt_email(data.email)
    email_hash = hash_email(data.email)
    password_hash = hash_password(data.password)
    phone_encrypted = encrypt_phone(data.phone) if data.phone else None
    phone_hash = hash_phone(data.phone) if data.phone else None
    language_id = data.language_id

    # Check if user is available
    result = await db.execute(
        text(
            """
            SELECT is_user_available(:username, :email_hash, :phone_hash) AS available
        """
        ),
        {"username": username, "email_hash": email_hash, "phone_hash": phone_hash},
    )
    available = result.scalar()

    if not available:
        raise HTTPException(409, "Username, email, or phone already exists")

    await db.execute(
        text(
            """
            CALL register_user(
                :username,
                :email_encrypted,
                :email_hash,
                :password_hash,
                :phone_encrypted,
                :phone_hash,
                :preferred_language_id
            )
            """
        ),
        {
            "username": username,
            "email_encrypted": email_encrypted,
            "email_hash": email_hash,
            "password_hash": password_hash,
            "phone_encrypted": phone_encrypted,
            "phone_hash": phone_hash,
            "preferred_language_id": language_id,
        },
    )
    await db.commit()
    return {"message": "User registered successfully", "username": username}
