from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserLogin2FA(BaseModel):
    otp_code: int
    token: str
