# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from os import getenv

from kfp import Client

MEMORY_REQUEST = getenv("MEMORY_REQUEST", "2G")
MEMORY_LIMIT = getenv("MEMORY_LIMIT", "4G")
CPU_REQUEST = getenv("CPU_REQUEST", "500m")
CPU_LIMIT = getenv("CPU_LIMIT", "2000m")
KF_PIPELINES_ENDPOINT = getenv("KF_PIPELINES_ENDPOINT", "0.0.0.0:31380/pipeline")
KF_PIPELINES_NAMESPACE = getenv("KF_PIPELINES_NAMESPACE", "deployments")
KFP_CLIENT = Client(
    host=KF_PIPELINES_ENDPOINT,
    namespace=KF_PIPELINES_NAMESPACE,
)
