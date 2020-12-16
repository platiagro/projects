# -*- coding: utf-8 -*-
"""Seldon utility functions."""
from kubernetes import client

from projects.kfp import KF_PIPELINES_NAMESPACE


def list_deployment_pods(deployment_id):
    """
    List pods under a deployment_id.

    Parameters
    ----------
    deployment_id : str

    Returns
    -------
    list
        A list of deployment's pod.

    Notes
    ----
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get pods -l app=deployment_name`.
    """
    core_api = client.CoreV1Api()
    objects_names = list_seldon_deployment_objects(deployment_id)

    for name in objects_names:
        pod_list = core_api.list_namespaced_pod(
            namespace=KF_PIPELINES_NAMESPACE,
            label_selector=f'app={name}'
        )

    return pod_list.items


def list_seldon_deployment_objects(deployment_id, namespace=None):
    """
    List Selon Deployment objects names by deployment_id.

    Parameters
    ----------
    deployment_id : str
    namespace : str
        The namespace used by Kubernetes. Default value is defined by the `KF_PIPELINES_NAMESPACE`
        environment variable.

    Returns
    -------
    list or Union[None, tuple, bool]
        Seldon Deployment objects names under a deployment.

    Notes
    -----
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get sdep deployment_id`.
    """
    objects = []
    custom_api = client.CustomObjectsApi()

    if not namespace:
        namespace = KF_PIPELINES_NAMESPACE

    objects = custom_api.get_namespaced_custom_object(
            group='machinelearning.seldon.io',
            version='v1',
            namespace=namespace,
            plural='seldondeployments',
            name=deployment_id,
    )
    objects = objects['status']['deploymentStatus'].keys()

    return objects
