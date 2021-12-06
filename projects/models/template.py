# -*- coding: utf-8 -*-
"""Template model."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, JSON, String, Text

from projects.database import Base
from projects.utils import TimeStamp, now


class Template(Base):
    __tablename__ = "templates"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    tasks = Column(JSON, nullable=False, default=[])
    experiment_id = Column(String(255), nullable=True)
    deployment_id = Column(String(255), nullable=True)
    created_at = Column(TimeStamp(), nullable=False, default=now())
    updated_at = Column(TimeStamp(), nullable=False, default=now())
    tenant = Column(String(255), nullable=True)
