# -*- coding: utf-8 -*-
"""Istio functions."""
import os
from kubernetes import client

from projects.kubernetes.kube_config import load_kube_config


def get_cluster_ip():
    """
    Retrieve the cluster ip.

    Returns
    -------
    str
        The cluster ip.
    """
    load_kube_config()
    v1 = client.CoreV1Api()

    service = v1.read_namespaced_service(
        name="istio-ingressgateway", namespace="istio-system")

    if service.status.load_balancer.ingress is None:
        cluster_ip = service.spec.cluster_ip
    else:
        if service.status.load_balancer.ingress[0].hostname:
            cluster_ip = service.status.load_balancer.ingress[0].hostname
        else:
            cluster_ip = service.status.load_balancer.ingress[0].ip
    return os.environ.get("INGRESS_HOST_PORT", cluster_ip)


def get_protocol():
    """
    Get protocol used by the cluster.

    Returns
    -------
    str
        The protocol.
    """
    load_kube_config()

    v1 = client.CustomObjectsApi()

    gateway = v1.get_namespaced_custom_object(
        group='networking.istio.io', version='v1alpha3', namespace='kubeflow',
        plural='gateways', name='kubeflow-gateway')

    if 'tls' in gateway['spec']['servers'][0]:
        protocol = 'https'
    else:
        protocol = 'http'

    return protocol
