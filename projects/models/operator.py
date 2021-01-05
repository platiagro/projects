# -*- coding: utf-8 -*-
"""Operator model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, ForeignKey, Float
from sqlalchemy.orm import backref, relationship

from projects.database import Base
from projects.utils import to_camel_case


class Operator(Base):
    __tablename__ = "operators"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False)
    dependencies = Column(JSON, nullable=True, default=[])
    parameters = Column(JSON, nullable=False, default={})
    position_x = Column("position_x", Float, nullable=True)
    position_y = Column("position_y", Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    task = relationship("Task", backref=backref("operator", uselist=False))

    def __repr__(self):
        return f"<Operator {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        status = getattr(self, "status", None)
        if status:
            d["status"] = status
        return d
