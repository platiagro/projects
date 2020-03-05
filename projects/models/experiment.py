# -*- coding: utf-8 -*-
"""Experiment model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .experiment_component import ExperimentComponent
from ..database import Base
from ..utils import to_camel_case


class Experiment(Base):
    __tablename__ = "experiments"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    project_id = Column(String(255), ForeignKey("projects.uuid"), nullable=False)
    dataset = Column(String(255))
    target = Column(String(255))
    position = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    components = relationship("ExperimentComponent", backref="experiment",
                              primaryjoin=uuid == ExperimentComponent.experiment_id)

    def __repr__(self):
        return "<Experiment {}>".format(self.name)

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        d["components"] = self.components
        return d
