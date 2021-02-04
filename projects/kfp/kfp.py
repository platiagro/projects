# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from os import getenv, makedirs, path
from pathlib import Path

from kfp import Client

MEMORY_REQUEST = getenv("MEMORY_REQUEST", "2G")
MEMORY_LIMIT = getenv("MEMORY_LIMIT", "10G")
CPU_REQUEST = getenv("CPU_REQUEST", "100m")
CPU_LIMIT = getenv("CPU_LIMIT", "2000m")
SELDON_REST_TIMEOUT = getenv("SELDON_REST_TIMEOUT", "60000")
SELDON_GRPC_TIMEOUT = getenv("SELDON_GRPC_TIMEOUT", "60000")
KF_PIPELINES_NAMESPACE = getenv("KF_PIPELINES_NAMESPACE", "anonymous")


def kfp_client():
    """
    Singleton that returns a kfp.Client object.
    It was changed from constant to a function because the client instance
    makes a request during __init__ (before the mock API is available), causing
    tests to fail.

    Returns
    -------
    kfp.Client
    """
    host = getenv("KF_PIPELINES_ENDPOINT", "ml-pipeline.kubeflow:8888")
    client = Client(host=host)
    # user namespace is stored in a configuration file at $HOME/.config/kfp/context.json
    makedirs(path.join(str(Path.home()), ".config", "kfp"), exist_ok=True)
    client.set_user_namespace(namespace=KF_PIPELINES_NAMESPACE)
    return client
