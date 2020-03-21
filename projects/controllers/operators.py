# -*- coding: utf-8 -*-
"""Operator controller."""
import sys
from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Operator
from .components import raise_if_component_does_not_exist
from .experiments import raise_if_experiment_does_not_exist
from .projects import raise_if_project_does_not_exist


def list_operators(project_id, experiment_id):
    """Lists all operators under an experiment.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.

    Returns:
        A list of all operator.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    operators = db_session.query(Operator) \
        .filter_by(experiment_id=experiment_id) \
        .order_by(Operator.position.asc()) \
        .all()
    return [operator.as_dict() for operator in operators]


def create_operator(project_id, experiment_id, component_id=None, **kwargs):
    """Creates a new operator in our database.

    The new operator is added to the end of the operator list.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        component_id (str): the component uuid.

    Returns:
        The operator info.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    if not isinstance(component_id, str):
        raise BadRequest("componentId is required")

    raise_if_component_does_not_exist(component_id)

    operator = Operator(uuid=str(uuid4()),
                        experiment_id=experiment_id,
                        component_id=component_id,
                        position=-1)    # use temporary position -1, fix_position below
    db_session.add(operator)
    db_session.commit()

    fix_positions(experiment_id=experiment_id,
                  operator_id=operator.uuid,
                  new_position=sys.maxsize)     # will add to end of list

    return operator.as_dict()


def update_operator(uuid, project_id, experiment_id, **kwargs):
    """Updates an operator in our database and adjusts the position of others.

    Args:
        uuid (str): the operator uuid to look for in our database.
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The operator info.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    operator = Operator.query.get(uuid)

    if operator is None:
        raise NotFound("The specified operator does not exist")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Operator).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    fix_positions(experiment_id=operator.experiment_id,
                  operator_id=operator.uuid,
                  new_position=operator.position)

    return operator.as_dict()


def delete_operator(uuid, project_id, experiment_id):
    """Delete an operator in our database.

    Args:
        uuid (str): the operator uuid to look for in our database.
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.

    Returns:
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    operator = Operator.query.get(uuid)

    if operator is None:
        raise NotFound("The specified operator does not exist")

    db_session.delete(operator)
    db_session.commit()

    fix_positions(experiment_id=operator.experiment_id)

    return {"message": "Operator deleted"}


def fix_positions(experiment_id, operator_id=None, new_position=-1):
    """Reorders the operators in an experiment when an operator is updated/deleted.

    Args:
        experiment_id (str): the experiment uuid.
        operator_id (str): the operator uuid.
        new_position (int): the position where the operator is shown.
    """
    other_operators = db_session.query(Operator) \
        .filter_by(experiment_id=experiment_id) \
        .filter(Operator.uuid != operator_id)\
        .order_by(Operator.position.asc()) \
        .all()

    if operator_id is not None:
        operator = Operator.query.get(operator_id)
        other_operators.insert(new_position, operator)

    for index, operator in enumerate(other_operators):
        data = {"position": index}
        db_session.query(Operator).filter_by(uuid=operator.uuid).update(data)
    db_session.commit()
