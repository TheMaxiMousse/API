import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

load_dotenv(".env")


class Envs:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


class BaseEmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    template_name: str
    body: Dict[str, Any]


class RegistrationEmailSchema(BaseEmailSchema):
    subject: str = "ChocoMax - Email Confirmation"
    template_name: str = "email_confirmation.html"


class PasswordResetEmailSchema(BaseEmailSchema):
    pass  # Add specific fields if needed


def send_email_background(background_tasks: BackgroundTasks, email: BaseEmailSchema):
    message = MessageSchema(
        subject=email.subject,
        recipients=email.email,
        template_body=email.body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name=email.template_name
    )
