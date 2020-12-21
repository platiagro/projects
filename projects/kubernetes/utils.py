# -*- coding: utf-8 -*-
"""Utility functions."""
from ast import literal_eval

from kubernetes import client
from kubernetes.client.rest import ApiException
from werkzeug.exceptions import InternalServerError

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


def get_pod_log(pod, container):
    """
    Read log of the specified Pod.

    Parameters
    ----------
    pod : kubernetes.client.models.v1_pod.V1Pod
    container : kubernetes.client.models.v1_container.V1Container

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
    pod_log = []

    try:
        pod_log = core_api.read_namespaced_pod_log(
                        name=pod.metadata.name,
                        namespace=KF_PIPELINES_NAMESPACE,
                        container=container.name,
                        pretty='true',
                        tail_lines=512,
                        timestamps=True
                    )

        return pod_log
    except ApiException as e:
        body = literal_eval(e.body)
        message = body['message']

        if 'ContainerCreating' in message:
            return pod_log
        raise InternalServerError(f"Error while trying to retrive container's log: {message}")
