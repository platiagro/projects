# -*- coding: utf-8 -*-
"""Email schema."""
from typing import List

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    emails: List[EmailStr]
