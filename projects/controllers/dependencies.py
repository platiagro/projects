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

    return [dependency.as_dict() for dependency in dependencies]


def create_dependency(operator_id, dependency):
    """Creates a new dependency in our database.

    Args:
        operator_id (str): the operator uuid.
        dependency (str): the dependency operator uuid.

    Returns:
        Dependency info.
    """

    dependency = Dependency(uuid=uuid_alpha(),
                            operator_id=operator_id,
                            dependency=dependency)
    db_session.add(dependency)
    db_session.commit()

    return dependency.as_dict()


def delete_dependency(uuid):
    """Delete an dependency in our database.

    Args:
        uuid (str): the dependency uuid to look for in our database.

    Returns:
        The deletion result.
    """
    dependency = Dependency.query.get(uuid)

    if dependency is None:
        raise NotFound("The specified dependency does not exist")

    db_session.delete(dependency)
    db_session.commit()

    return {"message": "Dependency deleted"}
