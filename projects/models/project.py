# -*- coding: utf-8 -*-
"""Project model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from projects.database import Base
from projects.models.deployment import Deployment
from projects.models.experiment import Experiment
from projects.kubernetes.seldon import list_project_seldon_deployments


class Project(Base):
    __tablename__ = "projects"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text)
    experiments = relationship("Experiment",
                               primaryjoin=uuid == Experiment.project_id,
                               lazy="joined")
    deployments = relationship("Deployment",
                               primaryjoin=uuid == Deployment.project_id,
                               lazy="joined")

    @hybrid_property
    def has_experiment(self):
        return True if self.experiments else False

    @hybrid_property
    def has_pre_deployment(self):
        return any([True for deployment in self.deployments])

    @hybrid_property
    def has_deployment(self):
        deployments = list_project_seldon_deployments(self.uuid)
        return True if deployments else False
