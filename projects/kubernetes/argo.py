# -*- coding: utf-8 -*-
"""Argo Workflows utility functions."""
import asyncio

from queue import Queue

from kubernetes.client.rest import ApiException
from kubernetes import client
from kubernetes.watch import Watch

from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config
EXCLUDE_CONTAINERS = ["istio-proxy", "wait"]


def list_workflows(run_id):
    """
    List workflow given a run_id.

    Parameters
    ----------
    run_id : str

    Returns
    -------
    list
        A list of workflows.

    Notes
    ----
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get workflow -l workflows.argoproj.io/workflow=type_-id_`.
    """
    load_kube_config()
    custom_api = client.CustomObjectsApi()

    workflows = custom_api.list_namespaced_custom_object(
        group="argoproj.io",
        version="v1alpha1",
        namespace=KF_PIPELINES_NAMESPACE,
        plural="workflows",
        label_selector=f"pipeline/runid={run_id}",
    )["items"]

    return workflows


def list_workflow_pods(run_id: str):
    """
    Lists pods from a workflow. Returns only pods that ran a platiagro task.

    Parameters
    ----------
    run_id : str

    Returns
    -------
    list
        A list of all logs from a run.
    """
    workflows = list_workflows(run_id)
    if len(workflows) == 0:
        return []

    workflow_name = workflows[0]["metadata"]["name"]

    load_kube_config()
    core_api = client.CoreV1Api()

    pod_list = core_api.list_namespaced_pod(
        namespace=KF_PIPELINES_NAMESPACE,
        label_selector=f"workflows.argoproj.io/workflow={workflow_name}",
    ).items

    # Filters by pods that have an annotation "name=...".
    # Only pods that ran a platiagro tasks have this annotation.
    pod_list = [pod for pod in pod_list if "name" in pod.metadata.annotations]

    return pod_list


async def watch_workflow_pods(run_id: str, queue):
    workflows = list_workflows(run_id)
    if len(workflows) == 0:
        return []

    workflow_name = workflows[0]["metadata"]["name"]

    load_kube_config()
    v1 = client.CoreV1Api()
    w = Watch()
    for pod in w.stream(v1.list_namespaced_pod,
                        namespace=KF_PIPELINES_NAMESPACE,
                        label_selector=f"workflows.argoproj.io/workflow={workflow_name}"):
        if pod["type"] == "ADDED":
            pod = pod["object"]
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS and "name" in pod.metadata.annotations:
                    print(f"added container {container.name} to queue {hex(id(queue))}")
                    await asyncio.create_task(log_stream(pod, container, queue))


async def log_stream(pod, container, queue):
    """
    Generates log stream of given pod's container.

    Parameters
    ----------
        pod: str
        container: str

    Yields
    ------
        str
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    w = Watch()
    pod_name = pod.metadata.name
    namespace = pod.metadata.namespace
    container_name = container.name
    try:
        for streamline in w.stream(
            v1.read_namespaced_pod_log,
            name=pod_name,
            namespace=namespace,
            container=container_name,
            pretty="true",
            tail_lines=0,
            timestamps=True
        ):
            await queue.put(streamline)

    except RuntimeError as e:
        logging.exception(e)
        return

    except asyncio.CancelledError as e:
        logging.exception(e)
        return
    except ApiException:
        """
        Expected behavior when trying to connect to a container that isn't ready yet.
        """
        pass
