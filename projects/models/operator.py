# -*- coding: utf-8 -*-
"""Operator model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import backref, relationship

from projects.database import Base


class Operator(Base):
    __tablename__ = "operators"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True, index=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=True, index=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False, index=True)
    dependencies = Column(JSON, nullable=True, default=[])
    parameters = Column(JSON, nullable=False, default={})
    status = Column(String(255), nullable=False, default="Unset")
    status_message = Column(String(255), nullable=True)
    position_x = Column("position_x", Float, nullable=True)
    position_y = Column("position_y", Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    task = relationship("Task", backref=backref("operator", uselist=False))
