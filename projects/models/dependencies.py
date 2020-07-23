# -*- coding: utf-8 -*-
"""Dependency model."""
from sqlalchemy import Column, String, ForeignKey

from ..database import Base
from ..utils import to_camel_case


class Dependency(Base):
    __tablename__ = "dependencies"
    uuid = Column(String(255), primary_key=True)
    operator_id = Column(String(255), ForeignKey("operators.uuid"), nullable=False)
    dependency = Column(String(255), ForeignKey("operators.uuid"), nullable=False)

    def __repr__(self):
        return f"<Dependency {self.uuid}>"

    def as_dict(self):
        d = {to_camel_case(c.name): getattr(self, c.name) for c in self.__table__.columns}
        return d
