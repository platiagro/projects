# -*- coding: utf-8 -*-
"""Parameters controller."""
from werkzeug.exceptions import NotFound

from projects.jupyter import read_parameters
from projects.models import Task


def list_parameters(task_id):
    """
    Lists all parameters from the experiment notebook of a task.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    list
        A list of all parameters.

    Raises
    ------
    NotFound
        When task_id does not exist.
    """
    task = Task.query.get(task_id)
    if task is None:
        raise NotFound("The specified task does not exist")

    return read_parameters(task.experiment_notebook_path)


def get_parameters_with_values(parameters):
    """
    Get parameters with values from operator.

    Parameters
    ----------
    parameters : list

    Returns
    -------
    list
        Operator parameters with values.
    """
    params = []

    for key, value in parameters.items():
        if value != '':
            params.append(key)

    return params


def remove_parameter(parameters, target):
    """
    Remove a specific parameter from a list of parameters.

    Parameters
    ----------
    parameters : list
    target : str
        The target to be removed.

    Returns
    -------
    list
        The new list.
    """
    params = []

    for parameter in parameters:
        if parameter["name"] != target:
            params.append(parameter)

    return params
