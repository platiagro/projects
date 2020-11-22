# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist


def list_logs(project_id, deployment_id, run_id):
    """
    Lists logs from a deployment run.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    dict
        A list of all logs from a run.

    Raises
    ------
    NotFound
        When any of project_id, deployment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    return []
