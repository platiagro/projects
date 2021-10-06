# -*- coding: utf-8 -*-
"""Seldon utility functions."""
import asyncio
import time

from asyncio import CancelledError
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.watch import Watch

from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.istio import get_cluster_ip, get_protocol
from projects.kubernetes.kube_config import load_kube_config

EXCLUDE_CONTAINERS = ["istio-proxy", "wait"]


def get_seldon_deployment_url(deployment_id, ip=None, protocol=None, external_url=True):
    """
    Get seldon deployment url.

    Parameters
    ----------
    deployment_id: str
    ip : str
        The cluster ip. Default value is None.
    protocol : str
        Either http or https. Default value is None.
    external_url : bool
        Whether to return the external url (Loadbalancer) or internal url.

    Returns
    -------
    str
        Seldon deployment url.

    Notes
    -----
    If the `ip` and `protocol` parameters are not given, it is recovered by Kubernetes resources.
    """
    if external_url:
        if not ip:
            ip = get_cluster_ip()

        if not protocol:
            protocol = get_protocol()

        return f"{protocol}://{ip}/seldon/{KF_PIPELINES_NAMESPACE}/{deployment_id}/api/v1.0/predictions"
    else:
        return f"http://{deployment_id}-model.{KF_PIPELINES_NAMESPACE}:8000/api/v1.0/predictions"


def list_deployment_pods(deployment_id):
    """
    List pods under a Deployment.

    Parameters
    ----------
    deployment_id : str

    Returns
    -------
    list
        A list of deployment's pod.

    Notes
    ----
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get pods -l seldon-deployment-id=deployment_id`.
    """
    load_kube_config()
    core_api = client.CoreV1Api()
    pod_list = core_api.list_namespaced_pod(
        namespace=KF_PIPELINES_NAMESPACE,
        label_selector=f"seldon-deployment-id={deployment_id}",
    ).items

    return pod_list


def list_project_seldon_deployments(project_id):
    """
    List deployments under a project.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    list
        A list of deployment's pod.
    """
    load_kube_config()
    custom_api = client.CustomObjectsApi()

    deployments = custom_api.list_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        namespace=KF_PIPELINES_NAMESPACE,
        plural="seldondeployments",
        label_selector=f"projectId={project_id}",
    )["items"]

    return deployments


def watch_deployment_pods(deployment_id, queue, event_loop,pool):
    load_kube_config()
    v1 = client.CoreV1Api()
    w = Watch()
    try:

        for pod in w.stream(
            v1.list_namespaced_pod,
            namespace=KF_PIPELINES_NAMESPACE,
            label_selector=f"seldon-deployment-id={deployment_id}",
        ):
            if pod["type"] == "ADDED":
                pod = pod["object"]
                for container in pod.spec.containers:
                    if container.name not in EXCLUDE_CONTAINERS:
                        print(f"added container {container.name} to queue {hex(id(queue))}")
                        event_loop.run_in_executor(pool, log_stream, pod, container, queue)
    except CancelledError:
        """
        Expected behavior when trying to cancel task
        """
        print("Stopping watcher")
        w.stop()
        return


def log_stream(pod, container, queue):
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
            timestamps=True,
        ):
            queue.put_nowait(streamline)

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
    except CancelledError:
        """
        Expected behavior when trying to cancel task
        """
        print("Stopping log watcher")
        return