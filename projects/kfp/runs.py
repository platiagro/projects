# -*- coding: utf-8 -*-
"""Kubeflow Pipelines Runs interface."""
import json
import os

from datetime import datetime
from werkzeug.exceptions import BadRequest

from projects.kfp import KFP_CLIENT
from projects.kfp.pipeline import compile_pipeline
from projects.kfp.utils import get_operator_parameters


def list_runs(experiment_id):
    """
    Lists all comparisons under a project.

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
        if workflow_manifest["metadata"]["generateName"] == "experiment-":
            run_id = kfp_run.id
            run = get_run(experiment_id=experiment_id,
                          run_id=run_id)

            runs.append(run)

    return runs


def start_run(experiment_id, operators):
    """
    Start a new run in Kubeflow Pipelines.

    Parameters
    ----------
    experiment_id : str
    operators : list

    Returns
    -------
    dict
        The run attributes.
    """
    compile_pipeline(name=experiment_id,
                     operators=operators)

    kfp_experiment = KFP_CLIENT.create_experiment(name=experiment_id)
    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")

    job_name = f"{experiment_id}-{tag}"
    pipeline_package_path = f"{experiment_id}.yaml"
    run = KFP_CLIENT.run_pipeline(
        experiment_id=kfp_experiment.id,
        job_name=job_name,
        pipeline_package_path=pipeline_package_path,
    )
    os.remove(pipeline_package_path)
    response = {"runId": run.id}
    creation_details = get_run(run.id, experiment_id)
    response.update(creation_details)

    return response


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

    # nodes are creating, returns the tasks with no dependencies as Pending
    if "nodes" not in workflow_manifest["status"]:
        template = next(t for t in workflow_manifest["spec"]["templates"] if t["name"] == "experiment")
        tasks = (t for t in template["dag"]["tasks"] if "dependencies" not in t)
        status = dict((t["name"], {"status": "Pending"}) for t in tasks)
        return {"operators": status}

    # nodes are running
    nodes = workflow_manifest["status"]["nodes"]

    operators_status = {}

    for index, node in enumerate(nodes.values()):
        if index != 0:
            display_name = str(node["displayName"])
            if "vol-tmp-data" != display_name:
                operator = {}
                # check if pipeline was interrupted
                if "message" in node and str(node["message"]) == "terminated":
                    operator["status"] = "Terminated"
                else:
                    operator["status"] = str(node["phase"])
                operator["parameters"] = get_operator_parameters(workflow_manifest, display_name)
                operators_status[display_name] = operator
    return {
        "operators": operators_status, "runId": kfp_run.run.id, "createdAt": kfp_run.run.created_at
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
        if workflow_manifest["metadata"]["generateName"] == "experiment-":
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
