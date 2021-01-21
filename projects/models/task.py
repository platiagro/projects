# -*- coding: utf-8 -*-
"""Task model."""
import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, JSON, String, Text
from sqlalchemy.sql import expression

from projects import __version__
from projects.database import Base

DEFAULT_IMAGE = os.getenv("TASK_DEFAULT_EXPERIMENT_IMAGE", f'platiagro/platiagro-experiment-image:{__version__}')


class Task(Base):
    __tablename__ = "tasks"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=False, default=DEFAULT_IMAGE)
    commands = Column(JSON, nullable=True)
    arguments = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=False, default=["DEFAULT"])
    parameters = Column(JSON, nullable=False, default=[])
    experiment_notebook_path = Column(String(255))
    deployment_notebook_path = Column(String(255), nullable=True)
    is_default = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
