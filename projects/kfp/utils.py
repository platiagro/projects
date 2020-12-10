# -*- coding: utf-8 -*-
"""Utility functions."""

import ast
import base64
import json
import yaml

from werkzeug.exceptions import InternalServerError
from kubernetes import config, client

from projects.kfp import KFP_CLIENT


def convert_parameter_value_to_correct_type(value):
    """
    Convert boolean and null JSON values to Python format.

    Parameters
    ----------
    value : str

    Returns
    -------
    str or None
    """
    if value == 'null':
        value = None
    elif value == 'true':
        value = True
    elif value == 'false':
        value = False
    else:
        try:
            # try to convert string to correct type
            value = ast.literal_eval(value)
        except Exception:
            pass
    return value


def format_operator_parameters(parameters):
    """
    Format operator parameters to human-readable.

    Parameters
    ----------
    parameters : list

    Returns
    -------
    dict
    """
    params = {}
    for parameter in parameters:
        if parameter != "" and parameter != "{}":
            parameter_slited = parameter.split(':')
            key = parameter_slited[0]
            value = parameter_slited[1].strip()
            if value.startswith('- '):
                params[key] = get_parameter_list_values(value)
            else:
                params[key] = convert_parameter_value_to_correct_type(value)
    return params


def get_parameter_list_values(value):
    """
    Retrieves a list of parameters values.

    Parameters
    ----------
    value : str

    Returns
    -------
    list
    """
    parameter_list_values = []
    list_values = value.split('-')
    for list_value in list_values:
        # Remove "from list_value and replace with empty
        list_value = list_value.replace('"', '')
        if list_value != "":
            """unicode_escape Encoding suitable as the contents of a Unicode literal in ASCII-encoded Python"""
            list_value = list_value.replace("\\/", "/").encode().decode('unicode_escape')
            parameter_list_values.append(list_value.strip())
    return parameter_list_values


def get_operator_parameters(workflow_manifest, operator):
    """
    retrieves all parameters associated with an operator.

    Parameters:
    ----------
    workflow_manifest : ?
    operator : str

    Returns
    -------
    list
    """
    templates = workflow_manifest['spec']['templates']
    for template in templates:
        name = template['name']
        if name == operator and 'container' in template and 'args' in template['container']:
            args = template['container']['args']
            for arg in args:
                if 'papermill' in arg:
                    # split the arg and get base64 parameters in fifth position
                    splited_arg = arg.split()
                    base64_parameters = splited_arg[4].replace(';', '')
                    # decode base64 parameters
                    parameters = base64.b64decode(base64_parameters).decode()
                    # replace \n- to make list parameter to be in same line
                    parameters = parameters.replace('\n-', '-').split('\n')
                    return format_operator_parameters(parameters)


def search_for_pod_info(details: dict, operator_id: str):
    """
    Get operator pod info, such as: name, status and message error (if failed).

    Parameters
    ----------
    details : dict
        Workflow manifest from pipeline runtime.
    operator_id : str

    Returns
    -------
    dict
        Pod informations.
    """
    info = {}

    try:
        if "nodes" in details["status"]:
            for node in [*details["status"]["nodes"].values()]:
                if node["displayName"] == operator_id:
                    info = {"name": node["id"], "status": node["phase"], "message": node["message"]}
    except KeyError:
        pass

    return info


def get_deployment_by_id(deployment_id):
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

    for seldon_deployment in list_deployments():
        if seldon_deployment["experimentId"] == deployment_id:
            deployment = seldon_deployment
            break

    return deployment


def list_deployments():
    """
    Get deployments list.

    Returns
    -------
    list
        Deployments list.
    """
    token = ""
    deployment_runs = []
    ip = get_cluster_ip()

    while True:
        list_runs = KFP_CLIENT.list_runs(
            page_token=token, sort_by="created_at desc", page_size=100)

        if list_runs.runs:
            runs = get_deployment_details(list_runs.runs, ip)
            deployment_runs.extend(runs)

            token = list_runs.next_page_token
            if token is None:
                break
        else:
            break

    return deployment_runs


def get_deployment_details(runs, ip):
    """
    Get deployments run list.

    Parameters
    ----------
    runs : list
    ip : str
        The cluster ip.

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
                experiment_id = deployment_details["experimentId"]

                created_at = deployment_details["createdAt"]
                deployment_details["createdAt"] = str(created_at.isoformat(
                    timespec='milliseconds')).replace('+00:00', 'Z')

                deployment_details["url"] = f"http://{ip}/seldon/deployments/{experiment_id}/api/v1.0/predictions"

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
        template = list(filter(lambda t: t['name'] == 'deployment', workflow_manifest['spec']['templates']))[0]
        deployment_manifest = yaml.load(template['resource']['manifest'], Loader=yaml.FullLoader)

        name = deployment_manifest['metadata']['name']
        if 'deploymentName' in deployment_manifest['metadata']:
            name = deployment_manifest['metadata']['deploymentName']
        return {
            'experimentId': experiment_id,
            'name': name,
            'status': run.status or 'Running',
            'createdAt': run.created_at,
            'runId': run.id
        }
    except IndexError:
        return {}


def get_cluster_ip():
    """
    Retrive the cluster ip.

    Returns
    -------
    str
        The cluster ip.
    """
    load_kube_config()
    v1 = client.CoreV1Api()

    service = v1.read_namespaced_service(
        name="istio-ingressgateway", namespace="istio-system")

    return service.status.load_balancer.ingress[0].ip


def load_kube_config():
    """
    Loads authentication and cluster information from Load kube-config file.

    Raises
    ------
    InternalServerError
        When the connection is not successfully established.

    Notes
    -----
    Default file location is `~/.kube/config`.
    """
    try:
        config.load_kube_config()
        success = True
    except Exception:
        success = False

    if success:
        return

    try:
        config.load_incluster_config()
    except Exception:
        raise InternalServerError("Failed to connect to cluster.")
