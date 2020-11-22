# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from string import Template

from kfp import compiler, dsl
from kubernetes import client as k8s_client
from kubernetes.client.models import V1PersistentVolumeClaim

from projects.kfp import KF_PIPELINES_NAMESPACE, MEMORY_REQUEST, MEMORY_LIMIT, \
    CPU_REQUEST, CPU_LIMIT


def compile_pipeline(name, operators):
    """
    Compile the pipeline in a .yaml file.

    Parameters
    ----------
    name : str
    operators : list
    """
    @dsl.pipeline(name="Experiment")
    def experiment_pipeline():
        pvc = V1PersistentVolumeClaim(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata={
                "name": f"vol-{name}",
                "namespace": KF_PIPELINES_NAMESPACE,
            },
            spec={
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": "1Gi",
                    },
                },
            },
        )

        wrkdirop = dsl.VolumeOp(
            name="vol-tmp-data",
            k8s_resource=pvc,
            action="apply",
        )

        # Create container_op for all operators
        containers = {}
        for operator in operators:
            container_op = create_container_op(operator)
            containers[operator.uuid] = container_op

        # Define operators volumes and dependecies
        for container_op in containers.values():
            dependencies = [containers[dependency_id] for dependency_id in operator.dependencies]
            container_op.after(*dependencies)

            container_op.add_pvolumes({"vol-tmp-data": wrkdirop.volume})

    compiler.Compiler() \
        .compile(experiment_pipeline, f"{name}.yaml")


def create_container_op(operator):
    """
    Create operator operator from YAML file.

    Parameters
    ----------
    operator : dict

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    arguments = []
    for argument in operator.task.arguments:
        ARG = Template(argument)
        argument = ARG.safe_substitute({
            "notebookPath": operator.task.experiment_notebook_path,
            "parameters": "",  # TODO
            "experimentId": operator.experiment_id,
            "operatorId": operator.uuid,
            "dataset": "",  # TODO
            "trainingDatasetDir": "",  # TRAINING_DATASETS_DIR,
        })
        arguments.append(argument)

    container_op = dsl.ContainerOp(
        name=operator.uuid,
        image=operator.task.image,
        command=operator.task.commands,
        arguments=arguments,
    )

    container_op.container.set_image_pull_policy("Always") \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="EXPERIMENT_ID",
                value=operator.experiment_id,
            ),
        ) \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="OPERATOR_ID",
                value=operator.uuid,
            ),
        ) \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="RUN_ID",
                value=dsl.RUN_ID_PLACEHOLDER,
            ),
        )

    container_op \
        .set_memory_request(MEMORY_REQUEST) \
        .set_memory_limit(MEMORY_LIMIT) \
        .set_cpu_request(CPU_REQUEST) \
        .set_cpu_limit(CPU_LIMIT)

    return container_op
