# -*- coding: utf-8 -*-
"""Template schema."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from projects.utils import to_camel_case


class TemplateBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class TemplateCreate(TemplateBase):
    name: str
    experiment_id: str


class TemplateUpdate(TemplateBase):
    name: Optional[str]


class Template(TemplateBase):
    uuid: str
    name: str
    tasks: List
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, model):
        return Template(
            uuid=model.uuid,
            name=model.name,
            tasks=model.tasks,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class TemplateList(BaseModel):
    templates: List[Template]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return TemplateList(
            templates=[Template.from_orm(model) for model in models],
            total=total,
        )
