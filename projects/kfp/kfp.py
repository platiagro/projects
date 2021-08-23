# -*- coding: utf-8 -*-
"""
Kubeflow Pipelines interface.
"""
from os import getenv, makedirs, path
from pathlib import Path

from kfp import Client

KF_PIPELINES_NAMESPACE = getenv("KF_PIPELINES_NAMESPACE", "anonymous")


def kfp_client(namespace=KF_PIPELINES_NAMESPACE):
    """
    Singleton that returns a kfp.Client object.
    It was changed from constant to a function because the client instance
    makes a request during __init__ (before the mock API is available), causing
    tests to fail.

    Parameters
    ----------
    namespace : str

    Returns
    -------
    kfp.Client
    """
    host = getenv("KF_PIPELINES_ENDPOINT", "http://ml-pipeline.kubeflow:8888")
    client = Client(host=host)
    if namespace != "kubeflow":
        # user namespace is stored in a configuration file at $HOME/.config/kfp/context.json
        makedirs(path.join(str(Path.home()), ".config", "kfp"), exist_ok=True)
        client.set_user_namespace(namespace=namespace)
    return client
