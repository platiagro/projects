import os
import warnings
from typing import List

from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, EmailStr

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_SENDER_ADDRESS = os.getenv("MAIL_SENDER_ADDRESS", "")
MAIL_SERVER = os.getenv("MAIL_SERVER", "")


class EmailSchema(BaseModel):
    email: List[EmailStr]

    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=MAIL_USERNAME,
            MAIL_PASSWORD=MAIL_PASSWORD,
            MAIL_FROM=MAIL_SENDER_ADDRESS,
            MAIL_PORT=587,
            MAIL_SERVER=MAIL_SERVER,
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True
        )
    except Exception as e:
        warnings.warn(f"Error while trying to config email schema:{e}")