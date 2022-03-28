# -*- coding: utf-8 -*-
"""Task schema."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, validator

from projects import validators
from projects.utils import to_camel_case


FORBIDDEN_CHARACTERS_REGEX = "[!*'():;@&=+$,\/?%#\[\]]"
MAX_CHARS_ALLOWED = 50


class TaskBase(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class TaskCreate(TaskBase):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    tags: Optional[List[str]]
    data_in: Optional[str]
    data_out: Optional[str]
    docs: Optional[str]
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
    category: Optional[str]
    tags: Optional[List[str]]
    data_in: Optional[str]
    data_out: Optional[str]
    docs: Optional[str]
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
    category: Optional[str]
    tags: Optional[List[str]]
    data_in: Optional[str]
    data_out: Optional[str]
    docs: Optional[str]
    image: Optional[str]
    parameters: List[Dict]
    cpu_limit: Optional[str]
    cpu_request: Optional[str]
    memory_limit: Optional[str]
    memory_request: Optional[str]
    created_at: datetime
    updated_at: datetime
    has_notebook: bool
    readiness_probe_initial_delay_seconds: Optional[int]

    @classmethod
    def from_orm(cls, model):
        return Task(
            uuid=model.uuid,
            name=model.name,
            description=model.description,
            commands=model.commands,
            arguments=model.arguments,
            category=model.category,
            tags=model.tags,
            data_in=model.data_in,
            data_out=model.data_out,
            docs=model.docs,
            image=model.image,
            parameters=model.parameters,
            cpu_limit=model.cpu_limit,
            cpu_request=model.cpu_request,
            memory_limit=model.memory_limit,
            memory_request=model.memory_request,
            created_at=model.created_at,
            updated_at=model.updated_at,
            has_notebook=model.has_notebook,
            readiness_probe_initial_delay_seconds=model.readiness_probe_initial_delay_seconds,
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


class TaskListRequest(BaseModel):
    filters: Optional[dict] = {}
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    order: Optional[str]

    @validator("filters")
    def validate_name_in_filters(cls, v):
        if v.get("name"):
            name = v.get("name")
            validators.raise_if_exceeded(MAX_CHARS_ALLOWED, name)
            validators.raise_if_forbidden_character(FORBIDDEN_CHARACTERS_REGEX, name)
            v["name"] = validators.escaped_format(name)
        return v
