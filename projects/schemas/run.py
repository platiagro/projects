# -*- coding: utf-8 -*-
"""Run schema."""
from datetime import datetime
from typing import List

from pydantic import BaseModel

from projects.schemas.operator import Operator
from projects.utils import to_camel_case


class RunBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class Run(RunBase):
    uuid: str
    operators: Dict
    created_at: datetime

    @classmethod
    def from_model(cls, model):
        return Run(
            uuid=model["uuid"],
            operators=model["operators"],
            created_at=model["createdAt"],
        )


class RunList(BaseModel):
    runs: List[Run]
    total: int

    @classmethod
    def from_model(cls, models, total):
        return RunList(
            runs=[Run.from_model(model) for model in models],
            total=total,
        )
