# -*- coding: utf-8 -*-
"""Seldon utility functions."""
from ast import literal_eval

from kubernetes import client
from kubernetes.client.rest import ApiException
from werkzeug.exceptions import InternalServerError

from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config


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
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get pods -l app=deployment_name`.
    """
    load_kube_config()
    core_api = client.CoreV1Api()
    objects_names = list_seldon_deployment_objects(deployment_id)
    pod_list = []

    for name in objects_names:
        pod_list = core_api.list_namespaced_pod(
            namespace=KF_PIPELINES_NAMESPACE,
            label_selector=f'app={name}'
        ).items

    return pod_list


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

    Raises
    ------
    InternalServerError
        While trying to query Kubernetes API.

    Notes
    -----
    Equivalent to `kubectl -n KF_PIPELINES_NAMESPACE get sdep deployment_id`.
    """
    load_kube_config()
    custom_api = client.CustomObjectsApi()
    objects = []

    if not namespace:
        namespace = KF_PIPELINES_NAMESPACE

    try:
        objects = custom_api.get_namespaced_custom_object(
                group='machinelearning.seldon.io',
                version='v1',
                namespace=namespace,
                plural='seldondeployments',
                name=deployment_id,
        )
        objects = objects['status']['deploymentStatus'].keys()

        return objects
    except ApiException as e:
        # Kubernetes takes a few seconds to create the requested object.
        # Check if the code raised is 404 (NotFound), otherwise, it's K8's error.
        body = literal_eval(e.body)
        message = body['message']

        if body['code'] == 404:
            return objects
        raise InternalServerError(f'Error while trying to retrive custom objects: {message}')
    except KeyError:
        # At this point, it's still being created,
        # and does not contain any `deploymentStatus` key yet.
        return objects
