# -*- coding: utf-8 -*-
"""Dependency controller."""
from ..database import db_session
from ..models import Dependency
from .utils import raise_if_operator_does_not_exist, uuid_alpha


def list_dependencies(operator_id):
    """Lists all dependencies under a operator.

    Args:
        operator_id (str): the operator uuid.

    Returns:
        A list of all dependencies.
    """
    raise_if_operator_does_not_exist(operator_id)

    dependencies = db_session.query(Dependency) \
        .filter_by(operator_id=operator_id) \
        .order_by(Dependency.uuid.asc()) \
        .all()

    return [dependency.as_dict()["dependency"] for dependency in dependencies]


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
