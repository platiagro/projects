# -*- coding: utf-8 -*-
"""Parameters controller."""
from projects import models
from projects.exceptions import NotFound


class ParameterController:
    def __init__(self, session):
        self.session = session

    def list_parameters(self, task_id: str):
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
        task = self.session.query(models.Task).get(task_id)
        if task is None:
            raise NotFound(
                code="TaskNotFound", message="The specified task does not exist"
            )

        return task.parameters
