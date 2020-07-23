# -*- coding: utf-8 -*-
"""Operator controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Operator
from .parameters import list_parameters
from .dependencies import list_dependencies, list_next_operators, \
    create_dependency, delete_dependency
from .utils import raise_if_component_does_not_exist, \
    raise_if_project_does_not_exist, raise_if_experiment_does_not_exist, \
    raise_if_operator_does_not_exist, uuid_alpha


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
        .all()

    response = []
    for operator in operators:
        check_status(operator)
        response.append(operator.as_dict())

    return response


def create_operator(project_id, experiment_id, component_id=None,
                    parameters=None, dependencies=None, **kwargs):
    """Creates a new operator in our database.

    The new operator is added to the end of the operator list.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        component_id (str): the component uuid.
        parameters (dict): the parameters dict.
        dependencies (list): the dependencies array.

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

    if dependencies is None:
        dependencies = []

    raise_if_dependencies_are_invalid(dependencies)

    operator = Operator(uuid=uuid_alpha(),
                        experiment_id=experiment_id,
                        component_id=component_id,
                        parameters=parameters)
    db_session.add(operator)
    db_session.commit()

    check_status(operator)

    operator_as_dict = operator.as_dict()

    update_dependencies(operator_as_dict['uuid'], dependencies)

    operator_as_dict["dependencies"] = dependencies

    return operator_as_dict


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

    dependencies = kwargs.pop("dependencies", None)

    if dependencies is not None:
        raise_if_dependencies_are_invalid(dependencies, operator_id=uuid)
        update_dependencies(uuid, dependencies)

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Operator).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

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

    operator_as_dict = operator.as_dict()
    delete_dependencies(operator_as_dict["uuid"], operator_as_dict["dependencies"])

    db_session.delete(operator)
    db_session.commit()

    return {"message": "Operator deleted"}


def update_dependencies(operator_id, new_dependencies):
    dependencies_raw = list_dependencies(operator_id)
    dependencies = [d['dependency'] for d in dependencies_raw]

    dependencies_to_add = [d for d in new_dependencies if d not in dependencies]
    dependencies_to_delete = [d for d in dependencies if d not in new_dependencies]

    for dependency in dependencies_to_add:
        create_dependency(operator_id, dependency)

    for dependency in dependencies_to_delete:
        for dependency_object in dependencies_raw:
            if dependency == dependency_object["dependency"]:
                delete_dependency(dependency_object["uuid"])
                break


def delete_dependencies(operator_id, dependencies):
    next_operators = list_next_operators(operator_id)

    for op in next_operators:
        op_dependencies_raw = list_dependencies(op)
        op_dependencies = [d["dependency"] for d in op_dependencies_raw]

        new_dependencies = dependencies + list(set(op_dependencies) - set(dependencies))
        new_dependencies.remove(operator_id)

        update_dependencies(op, new_dependencies)

    update_dependencies(operator_id, [])


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


def raise_if_dependencies_are_invalid(dependencies, operator_id=None):
    """Raises an exception if the specified dependencies are not valid.

    Args:
        dependencies (list): the dependencies list.
        operator_id (str): the operator uuid.
    """
    if not isinstance(dependencies, list):
        raise BadRequest("The specified dependencies are not valid.")

    for d in dependencies:
        try:
            raise_if_operator_does_not_exist(d)
            if d == operator_id:
                raise BadRequest("The specified dependencies are not valid.")
        except NotFound:
            raise BadRequest("The specified dependencies are not valid.")


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
