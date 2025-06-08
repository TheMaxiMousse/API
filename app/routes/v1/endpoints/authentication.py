from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.routes.v1.schemas.user.create import UserCreate
from app.utility.database import get_db
from app.utility.security import (
    encrypt_email,
    encrypt_phone,
    hash_email,
    hash_password,
    hash_phone,
)

router = APIRouter()


@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Endpoint for user registration."""
    user = User(
        username=data.username,
        email_encrypted=encrypt_email(data.email),
        email_hash=hash_email(data.email),
        password_hash=hash_password(data.password),
        phone_encrypted=encrypt_phone(data.phone) if data.phone else None,
        phone_hash=hash_phone(data.phone) if data.phone else None,
        language_id=data.language_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "User registered successfully", "user_id": str(user.user_id)}
