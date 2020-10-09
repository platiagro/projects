# -*- coding: utf-8 -*-
"""Training history model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, ForeignKey

from ..database import Base
from ..utils import to_camel_case


class TrainingHistory(Base):
    __tablename__ = "training_history"
    uuid = Column(String(255), primary_key=True)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=False)
    run_id = Column(String(255), nullable=False)
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingHistory {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        return d
