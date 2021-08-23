# -*- coding: utf-8 -*-
"""Task model."""
import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import expression

from sqlalchemy.ext.hybrid import hybrid_property

from projects import __version__
from projects.database import Base

TASK_DEFAULT_EXPERIMENT_IMAGE = os.getenv(
    "TASK_DEFAULT_EXPERIMENT_IMAGE",
    f"platiagro/platiagro-experiment-image:{__version__}",
)
TASK_DEFAULT_CPU_LIMIT = os.getenv("TASK_DEFAULT_CPU_LIMIT", "2000m")
TASK_DEFAULT_CPU_REQUEST = os.getenv("TASK_DEFAULT_CPU_REQUEST", "100m")
TASK_DEFAULT_MEMORY_LIMIT = os.getenv("TASK_DEFAULT_MEMORY_LIMIT", "10Gi")
TASK_DEFAULT_MEMORY_REQUEST = os.getenv("TASK_DEFAULT_MEMORY_REQUEST", "2Gi")


class Task(Base):
    __tablename__ = "tasks"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=False, default=TASK_DEFAULT_EXPERIMENT_IMAGE)
    commands = Column(JSON, nullable=True)
    arguments = Column(JSON, nullable=True)
    category = Column(String(255), nullable=False)
    tags = Column(JSON, nullable=True)
    data_in = Column(Text, nullable=True)
    data_out = Column(Text, nullable=True)
    docs = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=False, default=[])
    experiment_notebook_path = Column(String(255))
    deployment_notebook_path = Column(String(255), nullable=True)
    cpu_limit = Column(String(255), nullable=False, default=TASK_DEFAULT_CPU_LIMIT)
    cpu_request = Column(String(255), nullable=False, default=TASK_DEFAULT_CPU_REQUEST)
    memory_limit = Column(String(255), nullable=False, default=TASK_DEFAULT_MEMORY_LIMIT)
    memory_request = Column(String(255), nullable=False, default=TASK_DEFAULT_MEMORY_REQUEST)
    is_default = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @hybrid_property
    def has_notebook(self):
        return bool(self.experiment_notebook_path or self.deployment_notebook_path)
