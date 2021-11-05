# -*- coding: utf-8 -*-
"""Project model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from projects.database import Base
from projects.models.deployment import Deployment
from projects.models.experiment import Experiment
from projects.models.comparison import Comparison

CASCADE_BEHAVIOR = "all, delete-orphan"


class Project(Base):
    __tablename__ = "projects"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text)
    experiments = relationship("Experiment",
                               primaryjoin=uuid == Experiment.project_id,
                               lazy="joined",
                               cascade=CASCADE_BEHAVIOR)
    deployments = relationship("Deployment",
                               primaryjoin=uuid == Deployment.project_id,
                               lazy="joined",
                               cascade=CASCADE_BEHAVIOR)
    comparisons = relationship("Comparison",
                               primaryjoin=uuid == Comparison.project_id,
                               cascade=CASCADE_BEHAVIOR)

    tenant = Column(String(255), nullable=True)

    @hybrid_property
    def has_experiment(self):
        return len(self.experiments) > 0

    @hybrid_property
    def has_pre_deployment(self):
        return len(self.deployments) > 0

    @hybrid_property
    def has_deployment(self):
        return any(d.status == "Succeeded" and d.url is not None for d in self.deployments)
