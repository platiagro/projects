# -*- coding: utf-8 -*-
"""Message schema."""
from pydantic import BaseModel


class Message(BaseModel):
    message: str
