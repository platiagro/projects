# -*- coding: utf-8 -*-
"""Deployment schema."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from projects.schemas.operator import Operator
from projects.utils import to_camel_case


class DeploymentBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class DeploymentCreate(DeploymentBase):
    experiments: Optional[List[str]]
    template_id: Optional[str]
    copy_from: Optional[str]


class DeploymentUpdate(DeploymentBase):
    name: Optional[str]
    position: Optional[int]
    is_active: Optional[bool]


class Deployment(DeploymentBase):
    uuid: str
    name: str
    position: int
    is_active: bool
    experiment_id: Optional[str]
    project_id: str
    operators: List[Operator]
    created_at: datetime
    updated_at: datetime
    status: Optional[str]
    url: Optional[str]
    deployed_at: Optional[str]

    @classmethod
    def from_orm(cls, model):
        return Deployment(
            uuid=model.uuid,
            name=model.name,
            position=model.position,
            is_active=model.is_active,
            experiment_id=model.experiment_id,
            project_id=model.project_id,
            operators=model.operators,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class DeploymentList(BaseModel):
    deployments: List[Deployment]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return DeploymentList(
            deployments=[Deployment.from_orm(model) for model in models],
            total=total,
        )
