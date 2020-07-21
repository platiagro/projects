# -*- coding: utf-8 -*-
"""Experiment model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from .operators import Operator
from ..database import Base
from ..utils import to_camel_case


class Experiment(Base):
    __tablename__ = "experiments"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False)
    position = Column(Integer, nullable=False, default=-1)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    operators = relationship("Operator", backref="experiment",
                             primaryjoin=uuid == Operator.experiment_id)

    def __repr__(self):
        return f"<Experiment {self.name}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        d["operators"] = self.operators
        return d
