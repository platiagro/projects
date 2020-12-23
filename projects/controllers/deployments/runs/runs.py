# -*- coding: utf-8 -*-
"""Deployments Runs controller."""
from kubernetes import client
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist
from projects.models import Deployment

from projects.kfp import KFP_CLIENT
from projects.kfp import runs as kfp_runs
from projects.kfp.pipeline import undeploy_pipeline
from projects.kfp.deployments import get_deployment_runs

from projects.kubernetes.kube_config import load_kube_config


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

    runs = get_deployment_runs(deployment_id)

    return [runs]


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

    deployment = Deployment.query.get(deployment_id)

    if deployment is None:
        raise NOT_FOUND

    try:
        run = kfp_runs.start_run(operators=deployment.operators,
                                 experiment_id=deployment.experiment_id,
                                 deployment_id=deployment_id)
    except ValueError as e:
        raise BadRequest(str(e))

    run["deploymentId"] = deployment_id
    return run


def get_run(project_id, deployment_id, run_id):
    """
    Details a run in Kubeflow Pipelines.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    dict
        The run attributes.

    Raises
    ------
    NotFound
        When any of project_id, deployment_id, or run_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    run = get_deployment_runs(deployment_id)

    return run


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

    load_kube_config()
    api = client.CustomObjectsApi()
    custom_objects = api.list_namespaced_custom_object(
        "machinelearning.seldon.io",
        "v1alpha2",
        "deployments",
        "seldondeployments"
    )
    deployments_objects = custom_objects['items']

    if deployments_objects:
        for deployment in deployments_objects:
            if deployment['metadata']['name'] == deployment_id:
                undeploy_pipeline(deployment)

    deployment_run = get_deployment_runs(deployment_id)

    if not deployment_run:
        raise NotFound("Deployment run does not exist.")

    KFP_CLIENT.runs.delete_run(deployment_run["runId"])

    return {"message": "Deployment deleted."}
