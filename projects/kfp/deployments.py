# -*- coding: utf-8 -*-
"""Utility functions to handle deployment pipelines."""
import json
import yaml

from projects.kfp import KFP_CLIENT
from projects.kubernetes.istio import get_cluster_ip, get_protocol


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
        if deployment_run["experimentId"] == deployment_id:
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
        list_runs = KFP_CLIENT.list_runs(
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


def get_deployment_details(runs, ip=None, protocol=None):
    """
    Get deployments run list.

    Parameters
    ----------
    runs : list
    protocol : str
        Either http or https. Default value is None.
    ip : str
        The cluster ip. Default value is None.

    Returns
    -------
    list
        Deployment runs details.

    Notes
    -----
    If the `ip` and `protocol` parameters are not given, it is recovered by Kubernetes resources.
    """
    deployment_runs = []

    if not ip:
        ip = get_cluster_ip()

    if not protocol:
        protocol = get_protocol()

    for run in runs:
        manifest = run.pipeline_spec.workflow_manifest
        if "SeldonDeployment" in manifest:
            deployment_details = format_deployment_pipeline(run)
            if deployment_details:
                experiment_id = deployment_details['experimentId']

                created_at = deployment_details["createdAt"]
                deployment_details['createdAt'] = str(created_at.isoformat(
                    timespec='milliseconds')).replace('+00:00', 'Z')

                deployment_details['url'] = f'{protocol}://{ip}/seldon/deployments/{experiment_id}/api/v1.0/predictions'

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
        if "deploymentName" in deployment_manifest["metadata"]:
            name = deployment_manifest["metadata"]["deploymentName"]
        return {
            "experimentId": experiment_id,
            "name": name,
            "status": run.status or "Running",
            "createdAt": run.created_at,
            "runId": run.id
        }
    except (IndexError, KeyError):
        return {}
