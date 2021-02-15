# -*- coding: utf-8 -*-
"""Utility functions."""
from ast import literal_eval
from kubernetes import client
from kubernetes.client.rest import ApiException

from projects.exceptions import InternalServerError
from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config


def search_for_pod_info(details, operator_id):
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


def get_container_logs(pod, container):
    """
    Returns latest logs of the specified container.

    Parameters
    ----------
    pod : str
    container : str

    Returns
    -------
    str
        Container's logs.

    Raises
    ------
    InternalServerError
        While trying to query Kubernetes API.
    """
    load_kube_config()
    core_api = client.CoreV1Api()

    try:
        logs = core_api.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=KF_PIPELINES_NAMESPACE,
            container=container.name,
            pretty="true",
            tail_lines=512,
            timestamps=True,
        )

        return logs
    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]

        if "ContainerCreating" in message:
            return None
        raise InternalServerError(f"Error while trying to retrive container's log: {message}")


def volume_exists(name, namespace):
    """
    Returns whether a persistent volume exists.

    Parameters
    ----------
    name : str
    namespace : str

    Returns
    -------
    bool
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    try:
        volume = v1.read_namespaced_persistent_volume_claim(name=name, namespace=namespace)
        if volume.status.phase == "Bound":
            return True
        else:
            return False
    except ApiException:
        return False
