# -*- coding: utf-8 -*-
"""
A module that provides functions that handle volume operations.
"""
from kfp import dsl
from kfp.dsl._resource_op import kubernetes_resource_delete_op
from kubernetes.client.models import V1PersistentVolumeClaim


def create_volume_op(name: str, namespace: str, storage: str = "10Gi"):
    """
    Creates a kfp.dsl.VolumeOp container.

    Parameters
    ----------
    name : str
    namespace : str
    storage : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    pvc = V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata={
            "name": f"vol-{name}",
            "namespace": namespace,
        },
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": storage,
                },
            },
        },
    )

    return dsl.VolumeOp(
        name=f"vol-{name}",
        k8s_resource=pvc,
        action="apply",
    )


def delete_volume_op(name: str, namespace: str):
    """
    Creates a kfp.dsl.ContainerOp that deletes a volume (Kubernetes Resource).
    Parameters
    ----------
    name : str
    namespace : str
    Returns
    -------
    kfp.dsl.ContainerOp
    """
    kind = "PersistentVolumeClaim"
    return kubernetes_resource_delete_op(
        name=f"vol-{name}",
        kind=kind,
        namespace=namespace,
    )