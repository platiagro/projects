# -*- coding: utf-8 -*-
"""Prediction model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String

from projects.database import Base
from projects.utils import to_camel_case


class Prediction(Base):
    __tablename__ = "predictions"
    uuid = Column(String(255), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.uuid) for c in self.__table__.columns}
        return d