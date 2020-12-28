# -*- coding: utf-8 -*-
"""Experiments Figures controller."""
import platiagro

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist


def list_figures(project_id, experiment_id, run_id, operator_id):
    """
    Lists all figures from object storage as data URI scheme.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
        The run_id. If `run_id=latest`, then returns figures from the latest run_id.
    operator_id : str

    Returns
    -------
    list
        A list of data URIs.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, run_id, or operator_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    figures = platiagro.list_figures(experiment_id=experiment_id,
                                     operator_id=operator_id,
                                     run_id=run_id)
    return figures
