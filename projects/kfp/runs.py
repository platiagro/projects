# -*- coding: utf-8 -*-
"""Kubeflow Pipelines Runs interface."""
import json
import os

from datetime import datetime
from kfp_server_api.exceptions import ApiValueError
from werkzeug.exceptions import BadRequest

from projects.kfp import KFP_CLIENT
from projects.kfp.pipeline import compile_pipeline


def list_runs(experiment_id):
    """
    Lists all runs of an experiment.

    Parameters
    ----------
    experiment_id : str

    Returns
    -------
    list
        A list of all runs.
    """
    # In order to list_runs, we need to find KFP experiment id.
    # KFP experiment id is different from PlatIAgro's experiment_id,
    # so calling KFP_CLIENT.get_experiment(experiment_name='..') is required first.
    try:
        kfp_experiment = KFP_CLIENT.get_experiment(experiment_name=experiment_id)
    except ValueError:
        return []

    # Now, lists runs
    kfp_runs = KFP_CLIENT.list_runs(
        page_size="100",
        sort_by="created_at desc",
        experiment_id=kfp_experiment.id,
    )

    runs = []
    for kfp_run in kfp_runs.runs:
        workflow_manifest = json.loads(kfp_run.pipeline_spec.workflow_manifest)
        if workflow_manifest["metadata"]["generateName"] == f"experiment-{experiment_id}-":
            run_id = kfp_run.id
            run = get_run(experiment_id=experiment_id,
                          run_id=run_id)

            runs.append(run)

    return runs


def start_run(operators, experiment_id, deployment_id=None, deployment_name=None):
    """
    Start a new run in Kubeflow Pipelines.

    Parameters
    ----------
    operators : list
    experiment_id : str
    deployment_id : str or None
    deployment_name : str or None

    Returns
    -------
    dict
        The run attributes.
    """
    if len(operators) == 0:
        raise ValueError("Necessary at least one operator.")

    if deployment_id is None:
        name = f"experiment-{experiment_id}"
    else:
        name = f"deployment-{deployment_id}"

    if not deployment_name:
        deployment_name = deployment_id

    compile_pipeline(name=name,
                     operators=operators,
                     experiment_id=experiment_id,
                     deployment_id=deployment_id,
                     deployment_name=deployment_name)

    kfp_experiment = KFP_CLIENT.create_experiment(name=experiment_id)
    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")

    job_name = f"{name}-{tag}"
    pipeline_package_path = f"{name}.yaml"
    run = KFP_CLIENT.run_pipeline(
        experiment_id=kfp_experiment.id,
        job_name=job_name,
        pipeline_package_path=pipeline_package_path,
    )
    os.remove(pipeline_package_path)
    return get_run(run.id, experiment_id)


def get_run(run_id, experiment_id):
    """
    Details a run in Kubeflow Pipelines.

    Parameters
    ----------
    run_id : str
    experiment_id : str

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
        run_id = get_latest_run_id(experiment_id)

    kfp_run = KFP_CLIENT.get_run(
        run_id=run_id,
    )

    workflow_manifest = json.loads(kfp_run.pipeline_runtime.workflow_manifest)

    operators = {}

    # initializes all operators with status=Pending and parameters={}
    template = next(t for t in workflow_manifest["spec"]["templates"] if "dag" in t)
    tasks = (tsk for tsk in template["dag"]["tasks"] if not tsk["name"].startswith("vol-"))
    operators = dict((t["name"], {"status": "Pending", "parameters": {}}) for t in tasks)

    # set status for each operator
    for node in workflow_manifest["status"].get("nodes", {}).values():
        if node["displayName"] in operators:
            operator_id = node["displayName"]
            operators[operator_id]["status"] = get_status(node)

    # sets parameters for each operator
    for template in workflow_manifest["spec"]["templates"]:
        if "container" in template and "env" in template["container"]:
            operator_id = template["name"]
            operators[operator_id]["parameters"] = get_parameters(template)

    return {
        "uuid": kfp_run.run.id,
        "operators": operators,
        "createdAt": kfp_run.run.created_at,
    }


def get_latest_run_id(experiment_id):
    """
    Get the latest run id for an experiment.

    Parameters
    ----------
    experiment_id : str

    Returns
    -------
    str
    """
    try:
        kfp_experiment = KFP_CLIENT.get_experiment(experiment_name=experiment_id)
    except ValueError:
        return None

    # lists runs for trainings and deployments of an experiment
    kfp_runs = KFP_CLIENT.list_runs(
        page_size="100",
        sort_by="created_at desc",
        experiment_id=kfp_experiment.id,
    )

    # find the latest training run
    latest_run_id = None
    for kfp_run in kfp_runs.runs:
        workflow_manifest = json.loads(kfp_run.pipeline_spec.workflow_manifest)
        if workflow_manifest["metadata"]["generateName"] == f"experiment-{experiment_id}-":
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
        run_id = get_latest_run_id(experiment_id)

    KFP_CLIENT.runs.terminate_run(run_id=run_id)

    return {"message": "Run terminated."}


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
        run_id = get_latest_run_id(experiment_id)

    kfp_run = KFP_CLIENT.get_run(
        run_id=run_id,
    )

    if kfp_run.run.status == "Failed":
        KFP_CLIENT.runs.retry_run(run_id=kfp_run.run.id)
    else:
        raise BadRequest("Not a failed run")

    return {"message": "Run re-initiated successfully"}


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


def get_container_status(experiment_id, operator_id):
    """
    Get operator container status.

    Parameters
    ----------
    experiment_id : str
    operator_id : str

    Returns
    -------
    str
        The container status.
    """
    # always get the status from the latest run
    run_id = get_latest_run_id(experiment_id)

    try:
        kfp_run = KFP_CLIENT.get_run(
            run_id=run_id,
        )
        status = "Pending"
        workflow_manifest = json.loads(kfp_run.pipeline_runtime.workflow_manifest)

        for node in workflow_manifest["status"].get("nodes", {}).values():
            if node["displayName"] == operator_id:
                if "message" in node and str(node["message"]) == "terminated":
                    status = "Terminated"
                else:
                    status = str(node["phase"])
        return status
    except ApiValueError:
        return ""
