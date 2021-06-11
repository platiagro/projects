from pydantic import EmailStr, BaseModel
from fastapi_mail import ConnectionConfig
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]


    conf = ConnectionConfig(
        MAIL_USERNAME = " postmaster@sandbox7472bf2b72ea467e8e577e4ee53ca4dd.mailgun.org",
        MAIL_PASSWORD = "05966f90ce1132a11c8dc73f768f5d1b-90ac0eb7-3971aefc",
        MAIL_FROM = "aluifs@cpqd.com.br",
        MAIL_PORT = 587,
        MAIL_SERVER = "smtp.mailgun.org",
        MAIL_TLS = True,
        MAIL_SSL = False
)
