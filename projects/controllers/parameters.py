# -*- coding: utf-8 -*-
"""Parameters controller."""

from werkzeug.exceptions import NotFound

from ..models import Task
from ..jupyter import read_parameters


def list_parameters(task_id, is_checked=False):
    """Lists all parameters from the experiment notebook of a task.

    Args:
        task_id (str): the task uuid to look for in our database.

    Returns:
        A list of all parameters.
    """
    task = Task.query.get(task_id)
    if task is None:
        raise NotFound("The specified task does not exist")

    return read_parameters(task.experiment_notebook_path)
