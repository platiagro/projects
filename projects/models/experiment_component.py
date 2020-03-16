# -*- coding: utf-8 -*-
"""Experiment component model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from ..database import Base
from ..utils import to_camel_case


class ExperimentComponent(Base):
    __tablename__ = "experiment_components"
    uuid = Column(String(255), primary_key=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=False)
    component_id = Column(String(255), ForeignKey("components.uuid"), nullable=False)
    position = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<ExperimentComponent {}, {}>".format(self.experiment_id, self.component_id)

    def as_dict(self):
        return {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
