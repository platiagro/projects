# -*- coding: utf-8 -*-
"""Experiments Metrics controller."""
import platiagro
from werkzeug.exceptions import NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist


def list_metrics(project_id, experiment_id, run_id, operator_id):
    """
    Lists all metrics from object storage.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
        The run_id. If `run_id=latest`, then returns metrics from the latest run_id.
    operator_id : str

    Returns
    -------
    list
        A list of metrics.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, run_id, or operator_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    try:
        return platiagro.list_metrics(experiment_id=experiment_id,
                                      operator_id=operator_id,
                                      run_id=run_id)
    except FileNotFoundError as e:
        raise NotFound(str(e))
