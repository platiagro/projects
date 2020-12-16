# -*- coding: utf-8 -*-
"""Operator controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.tasks.parameters import list_parameters
from projects.controllers.utils import raise_if_task_does_not_exist, \
    raise_if_project_does_not_exist, raise_if_experiment_does_not_exist, \
    raise_if_operator_does_not_exist, uuid_alpha
from projects.database import db_session
from projects.models import Operator, Task


PARAMETERS_EXCEPTION_MSG = "The specified parameters are not valid"
DEPENDENCIES_EXCEPTION_MSG = "The specified dependencies are not valid."


def list_operators(project_id, experiment_id):
    """
    Lists all operators under an experiment.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    list
        A list of all operators.

    Raises
    ------
    NotFound
        When either project_id or experiment_id does not exist.
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


def create_operator(project_id, experiment_id, deployment_id=None,
                    task_id=None, parameters=None, dependencies=None,
                    position_x=None, position_y=None, **kwargs):
    """
    Creates a new operator in our database.
    The new operator is added to the end of the operator list.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    task_id :str
    parameters : dict
        The parameters dict.
    dependencies : list
        The dependencies array.
    position_x : float
        Position x.
    position_y : float
        Position y.
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The operator attributes.

    Raises
    ------
    BadRequest
        When task_id is not a str instance.
        When the `**kwargs` (task attributes) are invalid.
    NotFound
        When either project_id or experiment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    if experiment_id:
        raise_if_experiment_does_not_exist(experiment_id)

    if not isinstance(task_id, str):
        raise BadRequest("taskId is required")

    try:
        raise_if_task_does_not_exist(task_id)
    except NotFound as e:
        raise BadRequest(e.description)

    if parameters is None:
        parameters = {}

    raise_if_parameters_are_invalid(parameters)

    if dependencies is None:
        dependencies = []

    raise_if_dependencies_are_invalid(project_id, experiment_id, dependencies)

    operator = Operator(uuid=uuid_alpha(),
                        experiment_id=experiment_id,
                        deployment_id=deployment_id,
                        task_id=task_id,
                        dependencies=dependencies,
                        parameters=parameters,
                        position_x=position_x,
                        position_y=position_y)
    db_session.add(operator)
    db_session.commit()

    check_status(operator)

    return operator.as_dict()


def update_operator(project_id, experiment_id, operator_id, **kwargs):
    """
    Updates an operator in our database and adjusts the position of others.

    Parameters
    ----------
    project_id  :str
    experiment_id : str
    operator_id : str
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The operator attributes.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, or operator_id does not exist.
    BadRequest
        When the `**kwargs` (task attributes) are invalid.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    operator = Operator.query.get(operator_id)

    if operator is None:
        raise NotFound("The specified operator does not exist")

    raise_if_parameters_are_invalid(kwargs.get("parameters", {}))

    dependencies = kwargs.get("dependencies")
    if dependencies is not None:
        raise_if_dependencies_are_invalid(project_id, experiment_id, dependencies, operator_id=operator_id)

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Operator).filter_by(uuid=operator_id).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    check_status(operator)

    return operator.as_dict()


def delete_operator(project_id, experiment_id, operator_id):
    """
    Delete an operator in our database.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str

    Returns
    -------
    dict
        The deletion result.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, or operator_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    operator = Operator.query.get(operator_id)

    if operator is None:
        raise NotFound("The specified operator does not exist")

    # check if other operators contains the operator being deleted
    # in dependencies and remove this operator from dependencies
    operators = db_session.query(Operator) \
        .filter_by(experiment_id=experiment_id) \
        .filter(Operator.uuid != operator_id) \
        .all()
    for op in operators:
        if operator_id in op.dependencies:
            dependencies = op.dependencies.remove(operator_id)
            if dependencies is None:
                dependencies = []
            update_operator(project_id=project_id,
                            experiment_id=experiment_id,
                            operator_id=op.uuid,
                            dependencies=dependencies)

    db_session.delete(operator)
    db_session.commit()

    return {"message": "Operator deleted"}


def raise_if_parameters_are_invalid(parameters):
    """
    Raises an exception if the specified parameters are not valid.

    Parameters
    ----------
    parameters : dict

    Raises
    ------
    BadRequest
        When any parameter value is not str, int, float, bool, list, or dict.
    """
    if not isinstance(parameters, dict):
        raise BadRequest(PARAMETERS_EXCEPTION_MSG)

    for key, value in parameters.items():
        if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
            raise BadRequest(PARAMETERS_EXCEPTION_MSG)


def raise_if_dependencies_are_invalid(project_id, experiment_id, dependencies, operator_id=None):
    """
    Raises an exception if the specified dependencies are not valid.
    The invalid dependencies are duplicate elements on the dependencies,
    dependencies including the actual operator_id, dependencie's operator
    doesn't exist and ciclycal dependencies.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    dependencies : list
    operator_id : str

    Raises
    ------
    BadRequest
        When any dependency does not exist.
        When dependencies are cyclic.
    """
    if not isinstance(dependencies, list):
        raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

    # check if dependencies has duplicates
    if len(dependencies) != len(set(dependencies)):
        raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

    for d in dependencies:
        try:
            raise_if_operator_does_not_exist(d, experiment_id)
            if d == operator_id:
                raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)
        except NotFound:
            raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

    raise_if_has_cycles(project_id, experiment_id, operator_id, dependencies)


def raise_if_has_cycles(project_id, experiment_id, operator_id, dependencies):
    """
    Raises an exception if the dependencies of operators from experiment are cyclical.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    dependencies : list

    Raises
    ------
    BadRequest
        When dependencies are cyclic.
    """
    operators = list_operators(project_id, experiment_id)

    visited = dict.fromkeys([op['uuid'] for op in operators], False)
    recursion_stack = dict.fromkeys([op['uuid'] for op in operators], False)

    for op in operators:
        op_uuid = op["uuid"]
        if (visited[op_uuid] is False and
                has_cycles_util(op_uuid, visited, recursion_stack, dependencies, operator_id) is True):
            raise BadRequest("Cyclical dependencies.")
    return False


def has_cycles_util(operator_id, visited, recursion_stack, new_dependencies, new_dependencies_op):
    """
    Check if a run has cycle.

    Parameters
    ----------
    operator_id : str
    visited : bool
    recursion_stack : list
    new_dependencies :
    new_dependencies_op :

    Returns
    -------
    bool
        If a run has cycles or not.
    """
    visited[operator_id] = True
    recursion_stack[operator_id] = True

    operator = Operator.query.get(operator_id)
    dependencies = operator.dependencies

    if operator_id == new_dependencies_op:
        dependencies = dependencies + list(set(new_dependencies) - set(dependencies))

    # Recur for all neighbours
    # if any neighbour is visited and in
    # recursion_stack then graph is cyclic
    for neighbour in dependencies:
        if ((visited[neighbour] is False and
             has_cycles_util(neighbour, visited, recursion_stack, new_dependencies, new_dependencies_op) is True) or
                recursion_stack[neighbour] is True):
            return True

    recursion_stack[operator_id] = False
    return False


def check_status(operator):
    """
    Check operator status

    Parameters
    ----------
    operator : str

    Returns
    ------
    str
        The operator status.
    """
    # get total operator parameters with value
    op_params_keys = [key for key in operator.parameters.keys() if operator.parameters[key] != '']
    total_op_params = len(op_params_keys)

    task = Task.query.get(operator.task_id)
    if "DATASETS" not in task.tags:
        # get task parameters and remove dataset parameter
        comp_params = list_parameters(operator.task_id)
        comp_params = [parameter for parameter in comp_params if parameter['name'] != 'dataset']
        total_comp_params = len(comp_params)

        if total_op_params == total_comp_params:
            operator.status = 'Setted up'
        else:
            operator.status = 'Unset'
    else:
        if total_op_params == 1:
            operator.status = 'Setted up'
        else:
            operator.status = 'Unset'
