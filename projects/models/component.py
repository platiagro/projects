# -*- coding: utf-8 -*-
"""Component model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.sql import expression

from ..database import Base
from ..utils import to_camel_case


class Component(Base):
    __tablename__ = "components"
    uuid = Column(String(255), primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    training_notebook_path = Column(String(255))
    inference_notebook_path = Column(String(255))
    is_default = Column(Boolean, nullable=False, server_default=expression.false())
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Component {}>".format(self.name)

    def as_dict(self):
        return {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
