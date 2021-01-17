# -*- coding: utf-8 -*-
"""Template model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Text

from projects.database import Base


class Template(Base):
    __tablename__ = "templates"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    tasks = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
