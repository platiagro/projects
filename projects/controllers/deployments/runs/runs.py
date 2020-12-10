# -*- coding: utf-8 -*-
"""Deployments Runs controller."""
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist
from projects.kfp.pipeline import compile_pipeline
from projects.models import Deployment


NOT_FOUND = NotFound("The specified deployment does not exist")


def list_runs(project_id, deployment_id):
    """
    Lists all runs under a deployment.

    Parameters
    ----------
    project_id : str
    deployment_id : str

    Returns
    -------
    list
        A list of all runs from a deployment.

    Raises
    ------
    NotFound
        When either project_id or deployment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    return []


def create_run(project_id, deployment_id):
    """
    Starts a new run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    deployment_id : str

    Returns
    -------
    dict
        The run attributes.

    Raises
    ------
    NotFound
        When any of project_id, or deployment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    deployment = Deployment.query.get(deployment_id)
    if deployment is None:
        raise NOT_FOUND

    compile_pipeline(deployment.name, deployment.operators)

    return {"message": "Pipeline running."}


def terminate_run(project_id, deployment_id, run_id):
    """
    Terminates a run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    dict
        The termination result.

    Raises
    ------
    NotFound
        When any of project_id, deployment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    return {}
