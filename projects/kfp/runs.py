# -*- coding: utf-8 -*-
"""
Utility functions to access pipeline details.
"""
import json
from typing import Optional

from projects.exceptions import BadRequest
from projects.kfp import kfp_client


def list_runs(experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
    """
    Lists all runs of an experiment or deployment.

    Parameters
    ----------
    experiment_id : str or None
    deployment_id : str or None

    Returns
    -------
    list
        A list of all runs.
    """
    # In order to list_runs, we need first to find KFP experiment id.
    # KFP experiment id is different from PlatIAgro's experiment_id, and
    # KFP.experiment_name holds PlatIAgro's experiment_id / deployment_id.
    # so calling kfp_client().get_experiment(experiment_name='..') is required first.
    kfp_experiment = get_kfp_experiment(experiment_id, deployment_id)

    # Now, lists runs
    kfp_runs = kfp_client().list_runs(
        page_size="10",
        sort_by="created_at desc",
        experiment_id=kfp_experiment.id,
    )

    runs = []
    for kfp_run in kfp_runs.runs:
        run_id = kfp_run.id
        run = get_run(experiment_id=experiment_id,
                      run_id=run_id)
        runs.append(run)

    return runs


def get_run(run_id, experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
    """
    Details a run in Kubeflow Pipelines.

    Parameters
    ----------
    run_id : str
    experiment_id : str or None
    deployment_id : str or None

    Returns
    -------
    dict
        The run attributes.

    Raises
    ------
    ApiException
    ValueError
    """
    if run_id == "latest":
        run_id = get_latest_run_id(
            experiment_id=experiment_id,
            deployment_id=deployment_id,
        )

    kfp_run = kfp_client().get_run(
        run_id=run_id,
    )

    workflow_manifest = json.loads(kfp_run.pipeline_runtime.workflow_manifest)

    operators = {}

    workflow_status = workflow_manifest["status"].get("phase")

    if workflow_status in {"Succeeded", "Failed"}:
        default_node_status = "Unset"
    else:
        default_node_status = "Pending"

    # initializes all operators with status=Pending and parameters={}
    template = next(t for t in workflow_manifest["spec"]["templates"] if "dag" in t)
    tasks = (tsk for tsk in template["dag"]["tasks"] if not tsk["name"].startswith("vol-"))
    operators = dict((t["name"], {"status": default_node_status, "parameters": {}}) for t in tasks)

    # set status for each operator
    for node in workflow_manifest["status"].get("nodes", {}).values():
        if node["displayName"] in operators:
            operator_id = node["displayName"]
            operators[operator_id]["status"] = get_status(node)

    # sets taskId and parameters for each operator
    for template in workflow_manifest["spec"]["templates"]:
        operator_id = template["name"]
        if "inputs" in template and "parameters" in template["inputs"]:
            operators[operator_id]["taskId"] = get_task_id(template)
        if "container" in template and "env" in template["container"]:
            operators[operator_id]["parameters"] = get_parameters(template)

    return {
        "uuid": kfp_run.run.id,
        "operators": operators,
        "createdAt": kfp_run.run.created_at,
    }


def get_kfp_experiment(experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
    """
    Returns a Kubeflow Pipelines experiment for a given experiment/deployment.

    Parameters
    ----------
    experiment_id : str
    deployment_id : str

    Returns
    -------
    str
    """
    experiment_name = experiment_id or deployment_id
    try:
        return kfp_client().get_experiment(experiment_name=experiment_name)
    except ValueError:
        return None


def get_latest_run_id(experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
    """
    Get the latest run id for an experiment.

    Parameters
    ----------
    experiment_id : str

    Returns
    -------
    str
    """
    kfp_experiment = get_kfp_experiment(experiment_id, deployment_id)

    kfp_runs = kfp_client().list_runs(
        page_size="1",
        sort_by="created_at desc",
        experiment_id=kfp_experiment.id,
    )

    # find the latest training run
    latest_run_id = None
    for kfp_run in kfp_runs.runs:
        latest_run_id = kfp_run.id
        break

    return latest_run_id


def terminate_run(run_id, experiment_id):
    """
    Terminates a run in Kubeflow Pipelines.

    Parameters
    ----------
    run_id : str
    experiment_id : str

    Returns
    -------
    dict
        Deleted response confirmation.

    Raises
    ------
    ApiException
    """
    if run_id == "latest":
        run_id = get_latest_run_id(experiment_id=experiment_id)

    kfp_client().runs.terminate_run(run_id=run_id)

    return {"message": "Run terminated"}


def retry_run(run_id, experiment_id):
    """
    Retry a run in Kubeflow Pipelines.

    Parameters
    ----------
    run_id : str
    experiment_id : str

    Returns
    -------
    dict
        Retry response confirmation.

    Raises
    ------
    ApiException
    BadRequest
    """
    if run_id == "latest":
        run_id = get_latest_run_id(experiment_id=experiment_id)

    kfp_run = kfp_client().get_run(
        run_id=run_id,
    )

    if kfp_run.run.status == "Failed":
        kfp_client().runs.retry_run(run_id=kfp_run.run.id)
    else:
        raise BadRequest("Not a failed run")

    return {"message": "Run re-initiated successfully"}


def get_task_id(template):
    """
    Get task id from template input parameters.

    Parameters
    ----------
    template : dict

    Returns
    -------
    str
        Task id.
    """
    prefix = "vol-task-"
    suffix = "-name"
    for var in template["inputs"]["parameters"]:
        name = var["name"]
        if name.startswith(prefix):
            return name[len(prefix):len(name)-len(suffix)]


def get_parameters(template):
    """
    Builds a dict of parameters from a workflow manifest.

    Parameters
    ----------
    template : dict

    Returns
    -------
    dict
        Parameters.
    """
    parameters = {}
    prefix = "PARAMETER_"
    for var in template["container"]["env"]:
        name = var["name"]
        value = var.get("value")

        if name.startswith(prefix):
            name = name[len(prefix):]

            if value is not None:
                value = json.loads(value)

            parameters[name] = value

    return parameters


def get_status(node):
    """
    Builds a dict of status from a workflow manifest.

    Parameters
    ----------
    node : dict

    Returns
    -------
    str
    """
    # check if pipeline was interrupted
    if "message" in node and str(node["message"]) == "terminated":
        status = "Terminated"
    else:
        status = str(node["phase"])

    return status
