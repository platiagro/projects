# -*- coding: utf-8 -*-
"""Log schema."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from projects.utils import to_camel_case


class LogBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class Log(LogBase):
    level: str
    title: str
    message: str
    created_at: Optional[datetime]


class LogList(BaseModel):
    logs: List[Log]
    total: int
