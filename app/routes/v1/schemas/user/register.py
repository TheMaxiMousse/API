from pydantic import BaseModel


class UserRegister(BaseModel):
    token: str
    username: str
    password: str
    language_id: int | None = None
