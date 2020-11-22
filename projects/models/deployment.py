# -*- coding: utf-8 -*-
"""Deployment model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from projects.database import Base
from projects.models.operator import Operator
from projects.utils import to_camel_case


class Deployment(Base):
    __tablename__ = "deployments"
    uuid = Column(String(255), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    name = Column(Text, nullable=False)
    operators = relationship("Operator", primaryjoin=uuid == Operator.deployment_id)
    position = Column(Integer, nullable=False, default=-1)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Deployment {self.name}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        d["operators"] = [operator.as_dict() for operator in self.operators]
        d["status"] = None  # TODO
        return d
