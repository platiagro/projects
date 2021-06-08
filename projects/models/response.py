# -*- coding: utf-8 -*-
"""Response model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String

from projects.database import Base


class Response(Base):
    __tablename__ = "responses"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), nullable=False, index=True)
    body = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
