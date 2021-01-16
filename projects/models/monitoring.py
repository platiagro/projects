# -*- coding: utf-8 -*-
"""Monitoring model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String

from projects.database import Base
from projects.utils import to_camel_case


class Monitoring(Base):
    __tablename__ = "monitoring"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True, index=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Monitoring {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        return d
