# -*- coding: utf-8 -*-
"""Seldon utility functions."""
from typing import Optional

from kubernetes import client

from projects.kubernetes.istio import get_cluster_ip, get_protocol
from projects.kubernetes.kube_config import load_kube_config


def get_seldon_deployment_url(
    deployment_id: str,
    namespace: str,
    ip: Optional[str] = None,
    protocol: Optional[str] = None,
    external_url: Optional[bool] = True,
):
    """
    Get seldon deployment url.

    Parameters
    ----------
    deployment_id: str
    namespace : str
    ip : str, optional
        The cluster ip. Default value is None.
    protocol : str, optional
        Either http or https. Default value is None.
    external_url : bool, optional
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

        return f"{protocol}://{ip}/seldon/{namespace}/{deployment_id}/api/v1.0/predictions"
    else:
        return f"http://{deployment_id}-model.{namespace}:8000/api/v1.0/predictions"


def list_deployment_pods(deployment_id: str, namespace: Optional[str]):
    """
    List pods under a Deployment.

    Parameters
    ----------
    deployment_id : str
    namespace : str, optional

    Returns
    -------
    list
        A list of deployment's pod.

    Notes
    ----
    Equivalent to `kubectl -n namespace get pods -l seldon-deployment-id=deployment_id`.
    """
    load_kube_config()
    core_api = client.CoreV1Api()
    pod_list = core_api.list_namespaced_pod(
        namespace=namespace,
        label_selector=f'seldon-deployment-id={deployment_id}',
    ).items

    return pod_list
