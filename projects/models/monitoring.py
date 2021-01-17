# -*- coding: utf-8 -*-
"""Monitoring model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String

from projects.database import Base


class Monitoring(Base):
    __tablename__ = "monitoring"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True, index=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
