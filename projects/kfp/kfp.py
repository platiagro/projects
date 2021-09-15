# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
import os
import pathlib

import kfp

KF_PIPELINES_NAMESPACE = os.getenv("KF_PIPELINES_NAMESPACE", "anonymous")


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
    host = os.getenv("KF_PIPELINES_ENDPOINT", "http://ml-pipeline.kubeflow:8888")
    client = kfp.Client(host=host)
    if KF_PIPELINES_NAMESPACE != "kubeflow":
        # user namespace is stored in a configuration file at $HOME/.config/kfp/context.json
        os.makedirs(
            os.path.join(str(pathlib.Path.home()), ".config", "kfp"), exist_ok=True
        )
        client.set_user_namespace(namespace=KF_PIPELINES_NAMESPACE)
    return client
