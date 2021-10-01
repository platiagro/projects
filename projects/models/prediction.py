# -*- coding: utf-8 -*-
"""Prediction model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from projects.database import Base


class Prediction(Base):
    __tablename__ = "predictions"
    uuid = Column(String(255), primary_key=True)
    deployment_id = Column(String(255), nullable=False, index=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    status = Column(String(255), nullable=False, default="not_started")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
