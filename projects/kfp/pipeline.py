# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from base64 import b64encode
from string import Template
from yaml import dump

from kfp import compiler, dsl
from kubernetes import client as k8s_client
from kubernetes.client.models import V1PersistentVolumeClaim

from projects.kfp import KFP_CLIENT, KF_PIPELINES_NAMESPACE, MEMORY_REQUEST, \
    MEMORY_LIMIT, CPU_REQUEST, CPU_LIMIT


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
            "parameters": format_parameters_base64(operator.parameters),
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


def undeploy_pipeline(resource):
    """
    Undeploy a deployment pipeline.

    Parameters
    ----------
    resource : dict
        A k8s resource which will be submitted to the cluster.
    """
    @dsl.pipeline(name='Undeploy')
    def undeploy():
        dsl.ResourceOp(
            name='undeploy',
            k8s_resource=resource,
            action='delete'
        )

    KFP_CLIENT.create_run_from_pipeline_func(
        undeploy,
        {},
        run_name='undeploy',
        namespace=KF_PIPELINES_NAMESPACE
    )


def format_parameters_base64(parameters):
    """
    Format parameters to a format that papermill accepts: base64 encoded yaml.

    Parameters
    ----------
    parameters : dict

    Returns
    -------
    str:
        Base64-encoded YAML string, containing parameter values.
    """
    parameters_dict = {}
    for name, value in parameters.items():
        # "dataset" is a special parameter that contains a dataset filename
        # The prefix /tmp/data/ is added to the parameter so the notebook
        # receives the full path to the dataset file during a run.
        if name == "dataset":
            parameters_dict[name] = f"/tmp/data/{value}"
        else:
            parameters_dict[name] = value

    return b64encode(dump(parameters_dict).encode()).decode()
