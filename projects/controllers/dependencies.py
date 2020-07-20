# -*- coding: utf-8 -*-
"""Dependency controller."""
from ..database import db_session
from ..models import Dependency
from .utils import uuid_alpha


def create_dependency(operator_id, dependency_id):
    """Creates a new dependency in our database.

    Args:
        operator_id (str): the operator uuid.
        dependency_id (str): the dependency uuid.

    Returns:
        Dependency info.
    """

    dependency = Dependency(uuid=uuid_alpha(),
                            operator_id=operator_id,
                            dependency=dependency_id)
    db_session.add(dependency)
    db_session.commit()

    return dependency.as_dict()
