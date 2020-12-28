# -*- coding: utf-8 -*-
"""Kube-config functions."""
from kubernetes import config
from werkzeug.exceptions import InternalServerError


def load_kube_config():
    """
    Loads authentication and cluster information from Load kube-config file.

    Raises
    ------
    InternalServerError
        When the connection is not successfully established.

    Notes
    -----
    Default file location is `~/.kube/config`.
    """
    try:
        config.load_kube_config()
        success = True
    except Exception:
        success = False

    if success:
        return

    try:
        config.load_incluster_config()
    except Exception:
        raise InternalServerError("Failed to connect to cluster.")
