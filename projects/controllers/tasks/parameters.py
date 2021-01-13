# -*- coding: utf-8 -*-
"""Parameters controller."""
from werkzeug.exceptions import NotFound

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

    return task.parameters
