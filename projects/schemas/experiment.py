# -*- coding: utf-8 -*-
"""Experiment schema."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from projects import generic_validators
from projects.schemas.operator import Operator
from projects.utils import to_camel_case, MAX_CHARS_ALLOWED, FORBIDDEN_CHARACTERS_REGEX


class ExperimentBase(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class ExperimentCreate(ExperimentBase):
    name: str
    copy_from: Optional[str]

    @validator("name")
    def validate_name(cls, v):
        generic_validators.raise_if_exceeded(MAX_CHARS_ALLOWED, v)
        generic_validators.raise_if_forbidden_character(FORBIDDEN_CHARACTERS_REGEX, v)
        return v


class ExperimentUpdate(ExperimentBase):
    name: Optional[str]
    position: Optional[int]
    is_active: Optional[bool]
    template_id: Optional[str]


class Experiment(ExperimentBase):
    uuid: str
    name: str
    position: int
    is_active: bool
    project_id: str
    operators: List[Operator]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, model):
        return Experiment(
            uuid=model.uuid,
            name=model.name,
            position=model.position,
            is_active=model.is_active,
            project_id=model.project_id,
            operators=model.operators,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ExperimentList(BaseModel):
    experiments: List[Experiment]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return ExperimentList(
            experiments=[Experiment.from_orm(model) for model in models],
            total=total,
        )
