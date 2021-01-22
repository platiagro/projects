# -*- coding: utf-8 -*-
"""Task schema."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from projects.utils import to_camel_case


class TaskBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class TaskCreate(TaskBase):
    name: str
    description: Optional[str]
    tags: Optional[List[str]]
    copy_from: Optional[str]
    image: Optional[str]
    commands: Optional[str]
    arguments: Optional[str]
    parameters: Optional[List]
    experiment_notebook: Optional[Dict]
    deployment_notebook: Optional[Dict]
    is_default: Optional[bool]


class TaskUpdate(TaskBase):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    image: Optional[str]
    commands: Optional[str]
    arguments: Optional[str]
    parameters: Optional[List]
    experiment_notebook: Optional[Dict]
    deployment_notebook: Optional[Dict]


class Task(TaskBase):
    uuid: str
    name: str
    description: Optional[str]
    commands: Optional[List[str]]
    arguments: Optional[List[str]]
    tags: List[str]
    parameters: List[Dict]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model):
        return Task(
            uuid=model.uuid,
            name=model.name,
            description=model.description,
            commands=model.commands,
            arguments=model.arguments,
            tags=model.tags,
            parameters=model.parameters,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class TaskList(BaseModel):
    containerState: bool
    tasks: List[Task]
    total: int

    @classmethod
    def from_model(cls, containerState, models, total):
        return TaskList(
            containerState=containerState,
            tasks=[Task.from_model(model) for model in models],
            total=total,
        )
