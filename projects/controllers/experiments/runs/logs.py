# -*- coding: utf-8 -*-
"""Experiments Logs controller."""
from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist


def list_logs(project_id, experiment_id, run_id):
    """
    Lists logs from a experiment run.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
        The run_id. If `run_id=latest`, then returns logs from the latest run_id.

    Returns
    -------
    list
        A list of all logs from a run.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, run_id, or operator_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    return []
