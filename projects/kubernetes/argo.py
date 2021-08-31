# -*- coding: utf-8 -*-
"""Argo Workflows utility functions."""
from typing import Optional

from kubernetes import client

from projects.kubernetes.kube_config import load_kube_config


def list_workflows(run_id: str, namespace: Optional[str]):
    """
    List workflow given a run_id.

    Parameters
    ----------
    run_id : str
    namespace : str, optional

    Returns
    -------
    list
        A list of workflows.

    Notes
    ----
    Equivalent to `kubectl -n namespace get workflow -l workflows.argoproj.io/workflow=type_-id_`.
    """
    load_kube_config()
    custom_api = client.CustomObjectsApi()

    workflows = custom_api.list_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace=namespace,
            plural="workflows",
            label_selector=f"pipeline/runid={run_id}",
    )["items"]

    return workflows


def list_workflow_pods(run_id: str, namespace: Optional[str]):
    """
    Lists pods from a workflow. Returns only pods that ran a platiagro task.

    Parameters
    ----------
    run_id : str
    namespace : str, optional

    Returns
    -------
    list
        A list of all logs from a run.
    """
    workflows = list_workflows(run_id, namespace)
    if len(workflows) == 0:
        return []

    workflow_name = workflows[0]["metadata"]["name"]

    load_kube_config()
    core_api = client.CoreV1Api()

    pod_list = core_api.list_namespaced_pod(
        namespace=namespace,
        label_selector=f"workflows.argoproj.io/workflow={workflow_name}",
    ).items

    # Filters by pods that have an annotation "name=...".
    # Only pods that ran a platiagro tasks have this annotation.
    pod_list = [pod for pod in pod_list if "name" in pod.metadata.annotations]

    return pod_list
