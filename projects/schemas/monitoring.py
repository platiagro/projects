# -*- coding: utf-8 -*-
"""Monitoring schema."""
from datetime import datetime
from typing import List

from pydantic import BaseModel

from projects.utils import to_camel_case


class MonitoringBase(BaseModel):

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class MonitoringCreate(MonitoringBase):
    task_id: str


class MonitoringUpdate(MonitoringBase):
    pass


class Monitoring(MonitoringBase):
    uuid: str
    deployment_id: str
    task_id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model):
        return Monitoring(
            uuid=model.uuid,
            deployment_id=model.deployment_id,
            task_id=model.task_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class MonitoringList(BaseModel):
    monitorings: List[Monitoring]
    total: int

    @classmethod
    def from_model(cls, models, total):
        return MonitoringList(
            monitorings=[Monitoring.from_model(model) for model in models],
            total=total,
        )
