# -*- coding: utf-8 -*-
"""Project model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from projects.database import Base
from projects.utils import to_camel_case
from projects.kfp.deployments import get_deployment_runs


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
        d["hasExperiment"] = getattr(self, "hasExperiment", None)
        d["hasDeployment"] = getattr(self, "hasDeployment", None)
        d["hasPreDeployment"] = getattr(self, "hasPreDeployment", None)
        return d

    @hybrid_property
    def hasExperiment(self):
        return True if self.experiments else False

    @hybrid_property
    def hasDeployment(self):
        for experiment in self.experiments:
            for deployment in experiment.deployments:
                if get_deployment_runs(deployment.uuid):
                    return True
        return False

    @hybrid_property
    def hasPreDeployment(self):
        for experiment in self.experiments:
            if experiment.deployments:
                return True
        return False