# -*- coding: utf-8 -*-
"""Operator controller."""
from uuid import uuid4

from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Operator


def list_operators(project_id, experiment_id):
    """Lists all operators under an experiment.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.

    Returns:
        A list of all operator ids.
    """
    operators = Operator.query.filter_by(experiment_id=experiment_id)
    return sorted([operator.as_dict() for operator in operators], key=lambda e: e["position"])


def create_operator(project_id, experiment_id, component_id=None,
                    position=None, **kwargs):
    """Creates a new operator in our database.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        component_id (str): the component uuid.
        position (int, optional): the position where the operator is shown.

    Returns:
        The operator info.
    """
    if not isinstance(component_id, str):
        raise BadRequest("componentId is required")

    if not isinstance(position, int):
        raise BadRequest("position is required")

    operator = Operator(uuid=str(uuid4()),
                        experiment_id=experiment_id,
                        component_id=component_id,
                        position=position)
    db_session.add(operator)
    db_session.commit()

    fix_positions(experiment_id=experiment_id,
                  operator_id=operator.uuid,
                  new_position=position)

    return operator.as_dict()


def delete_operator(uuid):
    """Delete an operator in our database.

    Args:
        uuid (str): the operator uuid to look for in our database.

    Returns:
        The deletion result.
    """
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
        .filter(Operator.uuid != operator_id).all()

    if operator_id is not None:
        operator = Operator.query.get(operator_id)
        other_operators.insert(new_position, operator)

    for index, operator in enumerate(other_operators):
        data = {"position": index}
        db_session.query(Operator).filter_by(uuid=operator.uuid).update(data)
    db_session.commit()
