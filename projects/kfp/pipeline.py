# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from collections import defaultdict
from json import dumps, loads

from kfp import compiler, dsl
from kubernetes import client as k8s_client
from kubernetes.client.models import V1PersistentVolumeClaim

from projects.kfp import CPU_LIMIT, CPU_REQUEST, KFP_CLIENT, \
    KF_PIPELINES_NAMESPACE, MEMORY_LIMIT, MEMORY_REQUEST
from projects.kfp.templates import COMPONENT_SPEC, GRAPH, SELDON_DEPLOYMENT


def compile_pipeline(name, operators, is_deployment):
    """
    Compile the pipeline in a .yaml file.

    Parameters
    ----------
    name : str
    operators : list
    is_deployment : bool
    """
    @dsl.pipeline(name=name)
    def pipeline_func():
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

        # Find the special parameter "dataset" (which is copied to all operators)
        # The prefix /tmp/data/ is added to the parameter so the operator
        # receives the full path to the dataset file during a run.
        dataset = None
        for operator in operators:
            for parameter_name, parameter_value in operator.parameters.items():
                if parameter_name == "dataset":
                    dataset = f"/tmp/data/{parameter_value}"
                    break

        # Create container_op for all operators
        containers = {}
        for operator in operators:
            container_op = create_container_op(operator=operator,
                                               is_deployment=is_deployment,
                                               dataset=dataset)
            containers[operator.uuid] = (operator, container_op)

        # Define operators volumes and dependencies
        for operator, container_op in containers.values():
            dependencies = [containers[dependency_id][1] for dependency_id in operator.dependencies]
            container_op.after(*dependencies)

            container_op.add_pvolumes({"vol-tmp-data": wrkdirop.volume})

        if is_deployment:
            resource_op = create_resource_op(operators)

            for _, container_op in containers.values():
                resource_op.after(container_op)

    compiler.Compiler() \
        .compile(pipeline_func, f"{name}.yaml")


def create_container_op(operator, is_deployment, dataset=None):
    """
    Create kfp.dsl.ContainerOp container from an operator list.

    Parameters
    ----------
    operator : dict
    is_deployment: bool
    dataset : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    container_op = dsl.ContainerOp(
        name=operator.uuid,
        image=operator.task.image,
        command=operator.task.commands,
        arguments=operator.task.arguments,
    )

    if is_deployment:
        notebook_path = operator.task.deployment_notebook_path
    else:
        notebook_path = operator.task.experiment_notebook_path

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
        ) \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="NOTEBOOK_PATH",
                value=notebook_path,
            ),
        )

    if dataset is not None:
        dataset = dumps(dataset)

    container_op.container \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="PARAMETER_dataset",
                value=dataset,
            ),
        )

    for name, value in operator.parameters.items():
        if value is not None:
            # fix for: cannot unmarshal number into
            # Go struct field EnvVar.value of type string
            value = dumps(value)
        container_op.container \
            .add_env_variable(
                k8s_client.V1EnvVar(
                    name=f"PARAMETER_{name}",
                    value=value,
                ),
            )

    container_op.container \
        .set_memory_request(MEMORY_REQUEST) \
        .set_memory_limit(MEMORY_LIMIT) \
        .set_cpu_request(CPU_REQUEST) \
        .set_cpu_limit(CPU_LIMIT)

    return container_op


def create_resource_op(operators):
    """
    Create kfp.dsl.ResourceOp container from an operator list.

    Parameters
    ----------
    operators : list

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    component_specs = []
    for operator in operators:
        component_specs.append(
            COMPONENT_SPEC.substitute({
                "operatorId": operator.uuid,
                "experimentId": operator.deployment_id,
            })
        )

    first = None
    graph = defaultdict(list)
    for operator in operators:
        if len(operator.dependencies) == 0:
            first = operator.uuid

        for dependency_id in operator.dependencies:
            graph[dependency_id].append({operator.uuid: graph[operator.uuid]})

    if first is None:
        raise ValueError("deployment can't have cycles")

    def build_graph(operator_id, children):
        if len(children) > 1:
            raise ValueError("deployment can't have multiple dependencies")
        elif len(children) == 1:
            child_operator_id, children = children[0].items()
            children = build_graph(child_operator_id, children)
        else:
            children = "[]"

        return GRAPH.substitute({
            "name": operator_id,
            "children": children,
        })

    graph = build_graph(operator_id=first, children=graph[first])

    seldon_deployment = SELDON_DEPLOYMENT.substitute({
        "namespace": KF_PIPELINES_NAMESPACE,
        "deploymentName": name,
        "componentSpecs": ",".join(component_specs),
        "graph": graph,
    })

    seldon_deployment = loads(seldon_deployment)
    resource_op = dsl.ResourceOp(
        name="deployment",
        k8s_resource=seldon_deployment,
        success_condition="status.state == Available",
    ).set_timeout(300)

    return resource_op


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
