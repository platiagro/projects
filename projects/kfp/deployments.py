# -*- coding: utf-8 -*-
"""Utility functions to handle deployment pipelines."""
import json
import yaml

from projects.kfp import kfp_client
from projects.kubernetes.seldon import get_seldon_deployment_url


def get_deployment_runs(deployment_id):
    """
    Get deployment run by seldon deployment uuid.

    Parameters
    ----------
    deployment_id : str

    Returns
    -------
    dict
        The deployment details.
    """
    deployment = {}

    for deployment_run in list_deployments_runs():
        if deployment_run["deploymentId"] == deployment_id:
            deployment = deployment_run
            break
    return deployment


def list_deployments_runs():
    """
    Retrive runs associated with a deployment.

    Returns
    -------
    list
        Deployments runs list.
    """
    token = ""
    runs = []

    while True:
        list_runs = kfp_client().list_runs(
            page_token=token, sort_by="created_at desc", page_size=100)

        if list_runs.runs:
            runs_details = get_deployment_details(list_runs.runs)
            runs.extend(runs_details)

            token = list_runs.next_page_token
            if token is None:
                break
        else:
            break

    return runs


def get_deployment_details(runs):
    """
    Get deployments run list.

    Parameters
    ----------
    runs : list

    Returns
    -------
    list
        Deployment runs details.
    """
    deployment_runs = []

    for run in runs:
        manifest = run.pipeline_spec.workflow_manifest
        if "SeldonDeployment" in manifest:
            deployment_details = format_deployment_pipeline(run)
            if deployment_details:
                deployment_id = deployment_details["deploymentId"]

                created_at = deployment_details["createdAt"]
                deployment_details["createdAt"] = str(created_at.isoformat(
                    timespec="milliseconds")).replace("+00:00", "Z")

                deployment_details["url"] = get_seldon_deployment_url(deployment_id)

                deployment_runs.append(deployment_details)

    return deployment_runs


def format_deployment_pipeline(run):
    """
    Format deployment pipeline content.

    Parameters
    ----------
    run : kfp_server_api.models.api_run.ApiRun
        The deployment run.

    Returns
    -------
    dict
        A response formatted with the details of a deployment pipeline.
    """
    experiment_id = run.resource_references[0].name

    workflow_manifest = json.loads(
        run.pipeline_spec.workflow_manifest)

    try:
        template = list(filter(lambda t: t["name"] == "deployment", workflow_manifest["spec"]["templates"]))[0]
        deployment_manifest = yaml.load(template['resource']['manifest'], Loader=yaml.FullLoader)

        name = deployment_manifest["metadata"]["name"]
        deployment_id = deployment_manifest["metadata"]["deploymentId"]

        if "deploymentName" in deployment_manifest["metadata"]:
            name = deployment_manifest["metadata"]["deploymentName"]
        return {
            "experimentId": experiment_id,
            "name": name,
            "deploymentId": deployment_id,
            "status": run.status or "Running",
            "createdAt": run.created_at,
            "runId": run.id
        }
    except (IndexError, KeyError):
        return {}
