# -*- coding: utf-8 -*-
"""Template model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Text

from ..database import Base
from ..utils import to_camel_case


class Template(Base):
    __tablename__ = "templates"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    components = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Template {}>".format(self.name)

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        del d["components"]
        d["operators"] = [{"componentId": o, "position": i} for i, o in enumerate(self.components)]
        return d
