# -*- coding: utf-8 -*-
"""
Utility functions that start monitoring pipelines.
"""
import pkgutil

from datetime import datetime

import yaml
from jinja2 import Template
from kfp import dsl
from kfp.dsl._resource_op import kubernetes_resource_delete_op

from projects import models
from projects.kfp import kfp_client

TASK_VOLUME_MOUNT_PATH = "/home/jovyan"
MONITORING_SERVICE = Template(pkgutil.get_data("projects", "kfp/resources/MonitoringService.yaml").decode())
MONITORING_TRIGGER = Template(pkgutil.get_data("projects", "kfp/resources/MonitoringTrigger.yaml").decode())


def create_monitoring(monitoring: models.Monitoring, namespace: str):
    """
    Runs a Kubeflow Pipeline that creates K8s resources necessary for monitoring.

    Creates:
    - A KNative Service that runs a task using historical data.
    - A KNative Trigger that subscribes to responses that a seldondeployment produces
    and forwards them to the service.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Create Monitoring",
        description="A pipeline that creates all resources necessary for a new monitoring.",
    )
    def pipeline_func():
        monitoring_op = create_monitoring_op(monitoring=monitoring, namespace=namespace)
        create_trigger_op(monitoring=monitoring, namespace=namespace).after(monitoring_op)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{monitoring.task.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=monitoring.uuid,
        namespace=namespace,
    )


def delete_monitoring(monitoring: models.Monitoring, namespace: str):
    """
    Runs a Kubeflow Pipeline that deletes the knative service and trigger of a monitoring.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Delete Monitoring",
        description="A pipeline that deletes K8s resources associated with a given monitoring.",
    )
    def pipeline_func():
        trigger_op = delete_trigger_op(monitoring=monitoring, namespace=namespace)
        delete_monitoring_op(monitoring=monitoring, namespace=namespace).after(trigger_op)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{monitoring.task.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=monitoring.uuid,
    )


def create_monitoring_op(monitoring: models.Monitoring, namespace: str):
    """
    Creates a kfp.ResourceOp that creates a knative service for monitoring.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    k8s_resource = MONITORING_SERVICE.render(
        name=f"service-{monitoring.uuid}",
        namespace=namespace,
        monitoring_id=monitoring.uuid,
        experiment_id=monitoring.deployment.experiment_id,
        deployment_id=monitoring.deployment_id,
        configmap=f"configmap-{monitoring.task_id}",
    )
    k8s_resource = yaml.safe_load(k8s_resource)

    return dsl.ResourceOp(
        name=monitoring.task.name,
        k8s_resource=k8s_resource,
        action="create",
        success_condition="status.phase == Running",
        attribute_outputs={
            "name": "{.metadata.name}",
            "created_at": datetime.utcnow().isoformat(),
        },  # makes this ResourceOp to have a unique cache key
    )


def delete_monitoring_op(monitoring: models.Monitoring, namespace: str):
    """
    Creates a kfp.dsl.ContainerOp that deletes a knative service.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    kind = "services.serving.knative.dev"
    return kubernetes_resource_delete_op(
        name=monitoring.task.name,
        kind=kind,
        namespace=namespace,
    )


def create_trigger_op(monitoring: models.Monitoring, namespace: str):
    """
    Creates a kfp.ResourceOp that creates a knative eventing trigger for monitoring.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    k8s_resource = MONITORING_SERVICE.render(
        name=f"trigger-{monitoring.uuid}",
        namespace=namespace,
        deployment_id=monitoring.deployment_id,
        service=f"service-{monitoring.uuid}",
    )
    k8s_resource = yaml.safe_load(k8s_resource)

    return dsl.ResourceOp(
        name=monitoring.task.name,
        k8s_resource=k8s_resource,
        action="create",
        success_condition="status.phase == Running",
        attribute_outputs={
            "name": "{.metadata.name}",
            "created_at": datetime.utcnow().isoformat(),
        },  # makes this ResourceOp to have a unique cache key
    )


def delete_trigger_op(monitoring: models.Monitoring, namespace: str):
    """
    Creates a kfp.dsl.ContainerOp that deletes a knative eventing trigger.

    Parameters
    ----------
    monitoring : models.Monitoring
    namespace : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    kind = "triggers.eventing.knative.dev"
    return kubernetes_resource_delete_op(
        name=monitoring.task.name,
        kind=kind,
        namespace=namespace,
    )
