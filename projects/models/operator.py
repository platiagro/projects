# -*- coding: utf-8 -*-
"""Operator model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, ForeignKey, Float
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from projects.database import Base
from projects.kfp.runs import get_container_status
from projects.utils import get_parameters_with_values, remove_parameter


class Operator(Base):
    __tablename__ = "operators"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True, index=True)
    experiment_id = Column(String(255), ForeignKey("experiments.uuid"), nullable=True, index=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False, index=True)
    dependencies = Column(JSON, nullable=True, default=[])
    parameters = Column(JSON, nullable=False, default={})
    position_x = Column("position_x", Float, nullable=True)
    position_y = Column("position_y", Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    task = relationship("Task", backref=backref("operator", uselist=False))

    @hybrid_property
    def status(self):
        parameters = get_parameters_with_values(self.parameters)
        status = get_container_status(self.experiment_id, self.uuid)

        if status:
            return status
        elif "DATASETS" in self.task.tags:
            if parameters:
                status = "Setted up"
            else:
                status = "Unset"
        else:
            task_parameters = remove_parameter(self.task.parameters, "dataset")

            if len(parameters) == len(task_parameters):
                status = "Setted up"
            else:
                status = "Unset"

        return status
