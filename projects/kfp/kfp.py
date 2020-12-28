# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from os import getenv

from kfp import Client

MEMORY_REQUEST = getenv("MEMORY_REQUEST", "2G")
MEMORY_LIMIT = getenv("MEMORY_LIMIT", "10G")
CPU_REQUEST = getenv("CPU_REQUEST", "100m")
CPU_LIMIT = getenv("CPU_LIMIT", "2000m")
KF_PIPELINES_ENDPOINT = getenv("KF_PIPELINES_ENDPOINT", "ml-pipeline.deployments:8888")
KF_PIPELINES_NAMESPACE = getenv("KF_PIPELINES_NAMESPACE", "deployments")
KFP_CLIENT = Client(
    host=KF_PIPELINES_ENDPOINT,
    namespace=KF_PIPELINES_NAMESPACE,
)
