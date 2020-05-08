# -*- coding: utf-8 -*-
"""Project model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from ..database import Base
from ..utils import to_camel_case


class Project(Base):
    __tablename__ = "projects"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text)
    experiments = relationship("Experiment", lazy="joined")

    def __repr__(self):
        return f"<Project {self.name}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        d["experiments"] = self.experiments
        return d
