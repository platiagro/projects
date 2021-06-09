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
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    copy_from: Optional[str]
    image: Optional[str]
    commands: Optional[List[str]]
    arguments: Optional[List[str]]
    parameters: Optional[List]
    experiment_notebook: Optional[Dict]
    deployment_notebook: Optional[Dict]
    experiment_notebook_path: Optional[str]
    deployment_notebook_path: Optional[str]
    cpu_limit: Optional[str]
    cpu_request: Optional[str]
    memory_limit: Optional[str]
    memory_request: Optional[str]
    is_default: Optional[bool]


class TaskUpdate(TaskBase):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    image: Optional[str]
    commands: Optional[List[str]]
    arguments: Optional[List[str]]
    parameters: Optional[List]
    experiment_notebook: Optional[Dict]
    deployment_notebook: Optional[Dict]
    experiment_notebook_path: Optional[str]
    deployment_notebook_path: Optional[str]
    cpu_limit: Optional[str]
    cpu_request: Optional[str]
    memory_limit: Optional[str]
    memory_request: Optional[str]


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
    def from_orm(cls, model):
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
    tasks: List[Task]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return TaskList(
            tasks=[Task.from_orm(model) for model in models],
            total=total,
        )
