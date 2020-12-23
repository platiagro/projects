# -*- coding: utf-8 -*-
"""Experiments Runs controller."""
from kfp_server_api.rest import ApiException
from werkzeug.exceptions import NotFound

from projects.kfp import runs as kfp_runs
from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist
from projects.models import Experiment

NOT_FOUND = NotFound("The specified run does not exist")


def list_runs(project_id, experiment_id):
    """
    Lists all runs from an experiment.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    list
        A list of all runs from an experiment.

    Raises
    ------
    NotFound
        When either project_id or experiment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    runs = kfp_runs.list_runs(experiment_id=experiment_id)
    return runs


def create_run(project_id, experiment_id):
    """
    Starts a new run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    dict
        The run attributes.

    Raises
    ------
    NotFound
        When either project_id or experiment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(experiment_id)

    if experiment is None:
        raise NOT_FOUND

    run = kfp_runs.start_run(experiment_id=experiment_id,
                             operators=experiment.operators)
    run["experimentId"] = experiment_id
    return run


def get_run(project_id, experiment_id, run_id):
    """
    Details a run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    dict
        The run attributes.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    try:
        run = kfp_runs.get_run(experiment_id=experiment_id,
                               run_id=run_id)
    except (ApiException, ValueError):
        raise NOT_FOUND

    return run


def terminate_run(project_id, experiment_id, run_id):
    """
    Terminates a run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    dict
        The termination result.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    try:
        run = kfp_runs.terminate_run(experiment_id=experiment_id,
                                     run_id=run_id)
    except ApiException:
        raise NOT_FOUND

    return run


def retry_run(project_id, experiment_id, run_id):
    """
    Retry a run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    dict
        The retry result.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    try:
        run = kfp_runs.retry_run(experiment_id=experiment_id,
                                 run_id=run_id)
    except ApiException:
        raise NOT_FOUND

    return run
