import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = Column(String(50), unique=True, nullable=False)

    email_encrypted = Column(Text, nullable=False)
    email_hash = Column(Text, unique=True, nullable=False)
    is_email_verified = Column(Boolean, default=False)

    password_hash = Column(Text, nullable=False)

    phone_encrypted = Column(Text)
    phone_hash = Column(Text, unique=True)

    language_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_login_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
