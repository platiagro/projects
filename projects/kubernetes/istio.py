# -*- coding: utf-8 -*-
"""Istio functions."""
from kubernetes import client

from projects.kubernetes.kube_config import load_kube_config


def get_cluster_ip():
    """
    Retrive the cluster ip.

    Returns
    -------
    str
        The cluster ip.
    """
    load_kube_config()
    v1 = client.CoreV1Api()

    service = v1.read_namespaced_service(
        name='istio-ingressgateway', namespace='istio-system')

    return service.status.load_balancer.ingress[0].ip


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
