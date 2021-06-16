import os
import warnings
from typing import List

from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, EmailStr

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_SENDER_ADDRESS = os.getenv("MAIL_SENDER_ADDRESS", "")
MAIL_SERVER = os.getenv("MAIL_SERVER", "")
MAIL_PORT = os.getenv("MAIL_PORT", 587)
MAIL_TLS=os.getenv("MAIL_TLS", True)
MAIL_SSL=os.getenv("MAIL_SSL", False)

class EmailSchema(BaseModel):
    emails: List[EmailStr]

    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=MAIL_USERNAME,
            MAIL_PASSWORD=MAIL_PASSWORD,
            MAIL_FROM=MAIL_SENDER_ADDRESS,
            MAIL_PORT=MAIL_PORT,
            MAIL_SERVER=MAIL_SERVER,
            MAIL_TLS=MAIL_TLS,
            MAIL_SSL=MAIL_SSL,
            USE_CREDENTIALS=True
        )
    except Exception as e:
        warnings.warn(f"Error while trying to config email schema:{e}")
