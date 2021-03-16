# -*- coding: utf-8 -*-
"""Utility functions to handle monitorings."""
import warnings
from json import loads

from kfp import compiler, dsl
from kubernetes import client
from kubernetes.client.rest import ApiException

from projects.kfp import KF_PIPELINES_NAMESPACE, kfp_client
from projects.kfp.templates import DEPLOYMENT_BROKER, MONITORING_SERVICE, \
    MONITORING_TRIGGER
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
    except ApiException as e:
        warnings.warn(f"ConfigMap of task {task_id} not found, creating a new one.")


def create_deployment_broker(deployment_id):
    """
    Create a broker for given deployment_id.

    Parameters
    ----------
    deployment_id : str

    Returns
    -------
    str
        Broker name.
    """
    broker_name = f"broker-{deployment_id}"
    
    # Using nonlocal to acess variable on the parent scope
    @dsl.pipeline(name=broker_name)
    def broker():
        broker = DEPLOYMENT_BROKER.substitute({
            "broker": broker_name,
            "namespace": KF_PIPELINES_NAMESPACE,
        })
        broker_resource = loads(broker)
        dsl.ResourceOp(
            name=broker_name,
            k8s_resource=broker_resource,
            success_condition="status.conditions.3.status == True"

        )

    kfp_client().create_run_from_pipeline_func(
        broker,
        {},
        run_name="monitoring",
        namespace=KF_PIPELINES_NAMESPACE
    )

    return broker_name
    

def deploy_monitoring(deployment_id,
                      experiment_id,
                      run_id,
                      task_id,
                      broker_name):
    """
    Deploy a service and trigger for monitoring.

    Parameters
    ----------
    deployment_id : str
    experiment_id : str
    run_id : str
    task_id : str
    broker_name : str

    Returns
    -------
    dict
        The run attributes.
    """
    @dsl.pipeline(name="Monitoring")
    def monitoring():
        service_name = f"service-{task_id}"
        service = MONITORING_SERVICE.substitute({
            "name": service_name,
            "namespace": KF_PIPELINES_NAMESPACE,
            "taskId": task_id,
            "experimentId": experiment_id,
            "deploymentId": deployment_id,
            "runId": run_id
        })
        service_resource = loads(service)
        monitoring_service = dsl.ResourceOp(
            name=service_name,
            k8s_resource=service_resource,
            success_condition="status.conditions.1.status == True"
        )

        trigger = MONITORING_TRIGGER.substitute({
            "name": "monitoring_trigger",
            "namespace": KF_PIPELINES_NAMESPACE,
            "broker": broker_name,
            "service": service_name,
        })
        trigger_resource = loads(trigger)
        dsl.ResourceOp(
            name="monitoring_trigger",
            k8s_resource=trigger_resource,
            success_condition="status.conditions.2.status == True"
        ).after(monitoring_service)

    kfp_client().create_run_from_pipeline_func(
        monitoring,
        {},
        run_name="monitoring",
        namespace=KF_PIPELINES_NAMESPACE
    )
