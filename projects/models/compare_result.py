# -*- coding: utf-8 -*-
"""Compare result model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String

from projects.database import Base
from projects.utils import to_camel_case


class CompareResult(Base):
    __tablename__ = "compare_result"
    uuid = Column(String(255), primary_key=True)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"))
    operator_id = Column(String(255))
    active_tab = Column(String(10), nullable=False, default='1')
    run_id = Column(String(255))
    layout = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<CompareResult {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        return d
