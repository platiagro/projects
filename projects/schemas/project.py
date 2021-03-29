# -*- coding: utf-8 -*-
"""Project schema."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from projects.schemas.deployment import Deployment
from projects.schemas.experiment import Experiment
from projects.utils import to_camel_case


class ProjectBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class ProjectCreate(ProjectBase):
    name: str
    description: Optional[str]


class ProjectUpdate(ProjectBase):
    name: Optional[str]
    description: Optional[str]


class Project(ProjectBase):
    uuid: str
    name: str
    description: Optional[str]
    experiments: List[Experiment]
    deployments: List[Deployment]
    has_experiment: bool
    has_deployment: bool
    has_pre_deployment: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, model):
        return Project(
            uuid=model.uuid,
            name=model.name,
            description=model.description,
            experiments=model.experiments,
            deployments=model.deployments,
            has_experiment=model.has_experiment,
            has_deployment=model.has_deployment,
            has_pre_deployment=model.has_pre_deployment,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProjectList(BaseModel):
    projects: List[Project]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return ProjectList(
            projects=[Project.from_orm(model) for model in models],
            total=total,
        )
