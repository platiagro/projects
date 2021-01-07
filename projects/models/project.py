# -*- coding: utf-8 -*-
"""Project model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from projects.database import Base
from projects.kubernetes.seldon import list_project_seldon_deployments
from projects.utils import to_camel_case


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
        d["hasExperiment"] = self.hasExperiment
        d["hasPreDeployment"] = self.hasPreDeployment
        d["hasDeployment"] = self.hasDeployment
        return d

    @hybrid_property
    def hasExperiment(self):
        return True if self.experiments else False

    @hybrid_property
    def hasPreDeployment(self):
        return any([True for experiment in self.experiments if experiment.deployments])

    @hybrid_property
    def hasDeployment(self):
        deployments = list_project_seldon_deployments(self.uuid)
        return True if deployments else False
