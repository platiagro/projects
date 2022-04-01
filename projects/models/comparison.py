# -*- coding: utf-8 -*-
"""Comparison model."""
from sqlalchemy import Column, ForeignKey, JSON, String

from projects.database import Base
from projects.utils import TimeStamp, now


class Comparison(Base):
    __tablename__ = "comparisons"
    uuid = Column(String(255), primary_key=True)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False, index=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), index=True)
    operator_id = Column(String(255), index=True)
    active_tab = Column(String(10), nullable=False, default='1')
    run_id = Column(String(255))
    layout = Column(JSON)
    created_at = Column(TimeStamp(), nullable=False, default=now())
    updated_at = Column(TimeStamp(), nullable=False, default=now())
