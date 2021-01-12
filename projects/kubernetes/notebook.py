# -*- coding: utf-8 -*-
"""Kubeflow notebook server utility functions."""
from ast import literal_eval
from kubernetes import client
from kubernetes.client.rest import ApiException
from werkzeug.exceptions import InternalServerError

from projects.kubernetes.kube_config import load_kube_config

NOTEBOOK_NAMESPACE = "anonymous"
NOTEBOOK_NAME = "server"


def create_persistent_volume_claim(name, mount_path):
    """
    Creates a persistent volume claim and mounts it in the default notebook server.
    Parameters
    ----------
    name : str
    mount_path : str
    """
    load_kube_config()

    v1 = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()

    try:
        body = {
            "metadata": {
                "name": f"vol-{name}",
            },
            "spec": {
                "accessModes": [
                    "ReadWriteOnce",
                ],
                "resources": {
                    "requests": {
                        "storage": "10Gi",
                    },
                }
            },
        }
        v1.create_namespaced_persistent_volume_claim(
            namespace=NOTEBOOK_NAMESPACE,
            body=body,
        )

        body = [
            {
                "op": "add",
                "path": "/spec/template/spec/volumes/-",
                "value": {
                    "name": name,
                    "persistentVolumeClaim": {
                        "claimName": f"vol-{name}",
                    },
                },
            },
            {
                "op": "add",
                "path": "/spec/template/spec/containers/0/volumeMounts/-",
                "value": {
                    "mountPath": mount_path,
                    "name": name,
                },
            },
        ]

        custom_api.patch_namespaced_custom_object(
            group="kubeflow.org",
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            body=body,
        )
    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to patch notebook server: {message}")
