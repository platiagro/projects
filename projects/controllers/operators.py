# -*- coding: utf-8 -*-
"""Operator controller."""
import sys
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Operator
from .parameters import list_parameters
from .utils import raise_if_component_does_not_exist, \
    raise_if_project_does_not_exist, raise_if_experiment_does_not_exist, \
    uuid_alpha


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

    response = []
    for operator in operators:
        check_status(operator)
        response.append(operator.as_dict())

    return response


def create_operator(project_id, experiment_id, component_id=None,
                    parameters=None, **kwargs):
    """Creates a new operator in our database.

    The new operator is added to the end of the operator list.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        component_id (str): the component uuid.
        parameters (dict): the parameters dict.

    Returns:
        The operator info.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    if not isinstance(component_id, str):
        raise BadRequest("componentId is required")

    try:
        raise_if_component_does_not_exist(component_id)
    except NotFound as e:
        raise BadRequest(e.description)

    if parameters is None:
        parameters = {}

    raise_if_parameters_are_invalid(parameters)

    operator = Operator(uuid=uuid_alpha(),
                        experiment_id=experiment_id,
                        component_id=component_id,
                        position=-1,
                        parameters=parameters)  # use temporary position -1, fix_position below
    db_session.add(operator)
    db_session.commit()

    fix_positions(experiment_id=experiment_id,
                  operator_id=operator.uuid,
                  new_position=sys.maxsize)     # will add to end of list

    check_status(operator)

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

    raise_if_parameters_are_invalid(kwargs.get("parameters", {}))

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

    check_status(operator)

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


def raise_if_parameters_are_invalid(parameters):
    """Raises an exception if the specified parameters are not valid.

    Args:
        parameters (dict): the parameters dict.
    """
    if not isinstance(parameters, dict):
        raise BadRequest("The specified parameters are not valid")

    for key, value in parameters.items():
        if not isinstance(value, (str, int, float, bool, list, dict)):
            raise BadRequest("The specified parameters are not valid")


def check_status(operator):
    # get total operator parameters with value
    op_params_keys = [key for key in operator.parameters.keys() if operator.parameters[key] != '']
    total_op_params = len(op_params_keys)

    # get component parameters and remove dataset parameter
    comp_params = list_parameters(operator.component_id)
    total_comp_params = len(comp_params)

    if total_op_params == total_comp_params:
        operator.status = 'Setted up'
    else:
        operator.status = 'Unset'
