# -*- coding: utf-8 -*-
"""Operator model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, ForeignKey

from ..database import Base
from ..utils import to_camel_case


class Operator(Base):
    __tablename__ = "operators"
    uuid = Column(String(255), primary_key=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=False)
    component_id = Column(String(255), ForeignKey("components.uuid"), nullable=False)
    position = Column(Integer)
    parameters = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Operator {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        status = getattr(self, 'status', None)
        if status:
            d["status"] = status
        return d
