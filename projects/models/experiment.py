# -*- coding: utf-8 -*-
"""Experiment model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from projects.models.operator import Operator
from projects.models.deployment import Deployment
from projects.database import Base


class Experiment(Base):
    __tablename__ = "experiments"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=-1)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    operators = relationship("Operator",
                             backref="experiment",
                             primaryjoin=uuid == Operator.experiment_id,
                             lazy="joined",
                             cascade="all, delete-orphan")
    deployments = relationship("Deployment",
                               backref="experiment",
                               primaryjoin=uuid == Deployment.experiment_id,
                               lazy="joined")
