# -*- coding: utf-8 -*-
"""Comparison schema."""
import pytz
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from projects.utils import to_camel_case


class ComparisonBase(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class ComparisonUpdate(ComparisonBase):
    experiment_id: Optional[str]
    operator_id: Optional[str]
    run_id: Optional[str]
    active_tab: Optional[str]
    layout: Optional[Dict]


class Comparison(ComparisonBase):
    uuid: str
    created_at: datetime
    updated_at: datetime
    project_id: str
    experiment_id: Optional[str]
    operator_id: Optional[str]
    run_id: Optional[str]
    active_tab: str
    layout: Optional[Dict]

    @classmethod
    def from_orm(cls, model):
        return Comparison(
            uuid=model.uuid,
            created_at=model.created_at.replace(tzinfo=pytz.UTC),
            updated_at=model.updated_at.replace(tzinfo=pytz.UTC),
            project_id=model.project_id,
            experiment_id=model.experiment_id,
            operator_id=model.operator_id,
            run_id=model.run_id,
            active_tab=model.active_tab,
            layout=model.layout,
        )


class ComparisonList(BaseModel):
    comparisons: List[Comparison]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return ComparisonList(
            comparisons=[Comparison.from_orm(model) for model in models],
            total=total,
        )
