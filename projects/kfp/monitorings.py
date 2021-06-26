# -*- coding: utf-8 -*-
"""Utility functions to handle monitorings."""
import warnings
from json import loads

from kfp import dsl
from kubernetes import client
from kubernetes.client.rest import ApiException

from projects.exceptions import NotFound
from projects.kfp import KF_PIPELINES_NAMESPACE, kfp_client
from projects.kfp.pipeline import undeploy_pipeline
from projects.kfp.templates import MONITORING_SERVICE, MONITORING_TRIGGER
from projects.kubernetes.kube_config import load_kube_config


def create_monitoring_task_config_map(task_id, experiment_notebook_content):
    """
    Create a ConfigMap with the notebook of the given task.

    Parameters
    ----------
    task_id : str
    experiment_notebook_content : str
    """
    config_map_name = f"configmap-{task_id}"

    load_kube_config()
    v1 = client.CoreV1Api()

    body = {
        "metadata": {
            "name": config_map_name,
        },
        "data": {
            "Experiment.ipynb": experiment_notebook_content
        }
    }

    v1.create_namespaced_config_map(
        namespace=KF_PIPELINES_NAMESPACE,
        body=body,
    )

    warnings.warn(f"ConfigMap of task {task_id} created!")


def delete_monitoring_task_config_map(task_id):
    """
    Delete ConfigMap of the given task_id.

    Parameters
    ----------
    task_id : str
    """
    config_map_name = f"configmap-{task_id}"

    load_kube_config()
    v1 = client.CoreV1Api()
    try:
        v1.delete_namespaced_config_map(
            name=config_map_name,
            namespace=KF_PIPELINES_NAMESPACE
        )

        warnings.warn(f"ConfigMap of task {task_id} deleted!")
    except ApiException:
        warnings.warn(f"ConfigMap of task {task_id} not found, creating a new one.")


def deploy_monitoring(deployment_id,
                      experiment_id,
                      run_id,
                      task_id,
                      monitoring_id):
    """
    Deploy a service and trigger for monitoring.

    Parameters
    ----------
    deployment_id : str
    experiment_id : str
    run_id : str
    task_id : str
    monitoring_id : str

    Returns
    -------
    dict
        The run attributes.
    """
    @dsl.pipeline(name="Monitoring")
    def monitoring():
        service_name = f"service-{monitoring_id}"
        service = MONITORING_SERVICE.substitute({
            "name": service_name,
            "namespace": KF_PIPELINES_NAMESPACE,
            "monitoringId": monitoring_id,
            "experimentId": experiment_id,
            "deploymentId": deployment_id,
            "runId": run_id,
            "configMap": f"configmap-{task_id}"
        })
        service_resource = loads(service)
        monitoring_service = dsl.ResourceOp(
            name=service_name,
            k8s_resource=service_resource,
            success_condition="status.conditions.1.status == True",
            attribute_outputs={
                "monitoring_id": monitoring_id,
                "created_at": datetime.utcnow().isoformat(),
            },  # makes this ResourceOp to have a unique cache key
        )

        trigger_name = f"trigger-{monitoring_id}"
        trigger = MONITORING_TRIGGER.substitute({
            "name": trigger_name,
            "namespace": KF_PIPELINES_NAMESPACE,
            "deploymentId": deployment_id,
            "service": service_name,
        })
        trigger_resource = loads(trigger)
        trigger_op = dsl.ResourceOp(
            name="monitoring_trigger",
            k8s_resource=trigger_resource,
            success_condition="status.conditions.2.status == True",
            attribute_outputs={
                "monitoring_id": monitoring_id,
                "created_at": datetime.utcnow().isoformat(),
            },  # makes this ResourceOp to have a unique cache key
        ).after(monitoring_service)

    kfp_client().create_run_from_pipeline_func(
        monitoring,
        {},
        run_name="monitoring",
    )


def undeploy_monitoring(monitoring_id):
    """
    Undeploy the service and trigger of a given monitoring_id.

    Parameters
    ----------
    monitoring_id : str

    Raises
    ------
    NotFound
        When monitoring resources do not exist.
    """
    load_kube_config()
    api = client.CustomObjectsApi()

    try:
        # Undeploy service
        service_name = f"service-{monitoring_id}"
        service_custom_object = api.get_namespaced_custom_object(
            group="serving.knative.dev",
            version="v1alpha1",
            namespace=KF_PIPELINES_NAMESPACE,
            plural="services",
            name=service_name
        )

        undeploy_pipeline(service_custom_object)

        # Undeploy trigger
        trigger_name = f"trigger-{monitoring_id}"
        trigger_custom_object = api.get_namespaced_custom_object(
            group="eventing.knative.dev",
            version="v1alpha1",
            namespace=KF_PIPELINES_NAMESPACE,
            plural="triggers",
            name=trigger_name
        )

        undeploy_pipeline(trigger_custom_object)
    except ApiException:
        raise NotFound("Monitoring resources do not exist.")
