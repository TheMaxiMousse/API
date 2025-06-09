from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str | None = None
    language_iso_code: str | None = "en"
