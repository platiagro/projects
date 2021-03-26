# -*- coding: utf-8 -*-
"""Operator schema."""
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from projects.utils import to_camel_case


class OperatorBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class OperatorCreate(OperatorBase):
    task_id: str
    parameters: Optional[Dict]
    position_x: int
    position_y: int
    dependencies: Optional[List[str]]


class OperatorUpdate(OperatorBase):
    parameters: Optional[Dict]
    position_x: Optional[int]
    position_y: Optional[int]
    dependencies: Optional[List[str]]


class ParameterUpdate(BaseModel):
    value: Union[int, str, bool, float, List, None]


class Operator(OperatorBase):
    uuid: str
    task_id: str
    dependencies: List[str]
    parameters: Dict
    deployment_id: Optional[str]
    experiment_id: Optional[str]
    position_x: int
    position_y: int
    created_at: datetime
    updated_at: datetime
    status: str
    status_message: Optional[str]

    @classmethod
    def from_model(cls, model):
        return Operator(
            uuid=model.uuid,
            task_id=model.task_id,
            dependencies=model.dependencies,
            parameters=model.parameters,
            deployment_id=model.deployment_id,
            experiment_id=model.experiment_id,
            position_x=model.position_x,
            position_y=model.position_y,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=model.status,
            status_message=model.status_message,
        )


class OperatorList(BaseModel):
    operators: List[Operator]
    total: int

    @classmethod
    def from_model(cls, models, total):
        return OperatorList(
            operators=[Operator.from_model(model) for model in models],
            total=total,
        )
