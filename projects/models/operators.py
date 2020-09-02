# -*- coding: utf-8 -*-
"""Operator model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from .dependencies import Dependency
from ..database import Base
from ..utils import to_camel_case


class Operator(Base):
    __tablename__ = "operators"
    uuid = Column(String(255), primary_key=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=False)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False)
    parameters = Column(JSON, nullable=False, default={})
    position_x = Column('position_x', Float, nullable=True)
    position_y = Column('position_y', Float, nullable=True)
    dependencies = relationship("Dependency", primaryjoin=uuid == Dependency.operator_id)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Operator {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        status = getattr(self, 'status', None)
        d["dependencies"] = [dependency.as_dict()['dependency'] for dependency in self.dependencies]
        if status:
            d["status"] = status
        return d
