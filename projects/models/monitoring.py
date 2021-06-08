# -*- coding: utf-8 -*-
"""Monitoring model."""
from datetime import datetime
from warnings import warn

from sqlalchemy import Column, DateTime, event, \
    ForeignKey, String
from sqlalchemy.orm import relationship

from projects.database import Base
from projects.exceptions import NotFound
from projects.kfp import monitorings


class Monitoring(Base):
    __tablename__ = "monitorings"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), ForeignKey("deployments.uuid"), nullable=True, index=True)
    task_id = Column(String(255), ForeignKey("tasks.uuid"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    task = relationship("Task")


@event.listens_for(Monitoring, "after_delete")
def undeploy(_mapper, _connection, target):
    try:
        monitorings.undeploy_monitoring(monitoring_id=target.uuid)
    except NotFound as e:
        warn(e.message)
