from pydantic import EmailStr, BaseModel
from fastapi_mail import ConnectionConfig
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]


    conf = ConnectionConfig(
        MAIL_USERNAME = "",
        MAIL_PASSWORD = "",
        MAIL_FROM = "",
        MAIL_PORT = 587,
        MAIL_SERVER = "smtp.mailgun.org",
        MAIL_TLS = True,
        MAIL_SSL = False
)
