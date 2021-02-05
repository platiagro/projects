# -*- coding: utf-8 -*-
"""Kubeflow Pipelines interface."""
from collections import defaultdict
from json import dumps, loads
from os import getenv

from kfp import compiler, dsl
from kubernetes import client as k8s_client
from kubernetes.client.models import V1PersistentVolumeClaim

from projects import __version__
from projects.kfp import CPU_LIMIT, CPU_REQUEST, KF_PIPELINES_NAMESPACE, \
    MEMORY_LIMIT, MEMORY_REQUEST, SELDON_REST_TIMEOUT, kfp_client
from projects.kfp.templates import COMPONENT_SPEC, GRAPH, SELDON_DEPLOYMENT
from projects.kubernetes.utils import volume_exists

TASK_DEFAULT_DEPLOYMENT_IMAGE = getenv(
    "TASK_DEFAULT_DEPLOYMENT_IMAGE",
    f'platiagro/platiagro-deployment-image:{__version__}',
)


def compile_pipeline(name, operators, project_id, experiment_id, deployment_id, deployment_name):
    """
    Compile the pipeline in a .yaml file.

    Parameters
    ----------
    name : str
    operators : list
    project_id : str
    experiment_id : str
    deployment_id : str or None
    deployment_name : str
    """
    @dsl.pipeline(name=name)
    def pipeline_func():
        # Creates a volume to share data among container_ops
        volume_op_tmp_data = create_volume_op(name=f"tmp-data-{experiment_id}")

        # Gets dataset from any operator that has a dataset
        dataset = get_dataset(operators)

        # Creates a container_op for each operator
        containers = {}
        for operator in operators:
            if deployment_id is not None:
                notebook_path = operator.task.deployment_notebook_path
            else:
                notebook_path = operator.task.experiment_notebook_path

            container_op = create_container_op(operator=operator,
                                               experiment_id=experiment_id,
                                               notebook_path=notebook_path,
                                               dataset=dataset)
            containers[operator.uuid] = (operator, container_op)

        if deployment_id is not None:
            # Creates resource_op that creates a seldondeployment
            resource_op = create_resource_op(operators=operators,
                                             project_id=project_id,
                                             experiment_id=experiment_id,
                                             deployment_id=deployment_id,
                                             deployment_name=deployment_name)

        # Sets dependencies for each container_op
        for operator, container_op in containers.values():
            dependencies = [containers[dependency_id][1] for dependency_id in operator.dependencies]
            container_op.after(*dependencies)

            # data volume
            container_op.add_pvolumes({"/tmp/data": volume_op_tmp_data.volume})

            # task volume
            volume_op_home_jovyan = create_volume_op(name=f"task-{operator.task_id}")
            container_op.add_pvolumes({"/home/jovyan": volume_op_home_jovyan.volume})

            if deployment_id is not None:
                resource_op.after(container_op)

    compiler.Compiler() \
        .compile(pipeline_func, f"{name}.yaml")


def create_volume_op(name):
    """
    Creates a kfp.dsl.VolumeOp container.

    Parameters
    ----------
    name : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
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
                    "storage": "10Gi",
                },
            },
        },
    )

    volume_op = dsl.VolumeOp(
        name=f"vol-{name}",
        k8s_resource=pvc,
        action="apply",
    )

    return volume_op


def create_container_op(operator, experiment_id, notebook_path=None, dataset=None):
    """
    Create kfp.dsl.ContainerOp container from an operator list.

    Parameters
    ----------
    operator : dict
    experiment_id : str
    notebook_path : str or None
    dataset : str or None

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

    container_op.add_pod_annotation(name='name', value=operator.task.name)

    container_op.container.set_image_pull_policy("IfNotPresent") \
        .add_env_variable(
            k8s_client.V1EnvVar(
                name="EXPERIMENT_ID",
                value=experiment_id,
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
        # format multipe parameter
        task_parameter = get_task_parameter(operator.task.parameters, name)
        if task_parameter:
            parameter_multiple = task_parameter.get('multiple', False)
            if parameter_multiple and (value is None or not value):
                value = []
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


def create_resource_op(operators, project_id, experiment_id, deployment_id, deployment_name):
    """
    Create kfp.dsl.ResourceOp container from an operator list.

    Parameters
    ----------
    operators : list
    project_id : str
    experiment_id : str
    deployment_id : str
    deployment_name : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    component_specs = []
    tasks = {}

    for operator in operators:
        tasks.update({operator.uuid: operator.task_id})
        component_specs.append(
            COMPONENT_SPEC.substitute({
                "image": TASK_DEFAULT_DEPLOYMENT_IMAGE,
                "operatorId": operator.uuid,
                "experimentId": experiment_id,
                "deploymentId": deployment_id,
                "taskId": operator.task.uuid,
                "memoryRequest": MEMORY_REQUEST,
                "memoryLimit": MEMORY_LIMIT,
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
            child_operator_id, children = next(iter(children[0].items()))
            children = build_graph(child_operator_id, children)
        else:
            children = ""

        return GRAPH.substitute({
            "name": operator_id,
            "children": children,
        })

    graph = build_graph(operator_id=first, children=graph[first])

    seldon_deployment = SELDON_DEPLOYMENT.substitute({
        "namespace": KF_PIPELINES_NAMESPACE,
        "deploymentId": deployment_id,
        "componentSpecs": ",".join(component_specs),
        "graph": graph,
        "projectId": project_id,
        "tasks": dumps(tasks),
        "restTimeout": SELDON_REST_TIMEOUT,
    })

    sdep_resource = loads(seldon_deployment)

    # mounts the "/tmp/data" volume from experiment (if exists)
    sdep_resource = mount_volume_from_experiment(sdep_resource, experiment_id)

    resource_op = dsl.ResourceOp(
        name="deployment",
        k8s_resource=sdep_resource,
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
    @dsl.pipeline(name="Undeploy")
    def undeploy():
        dsl.ResourceOp(
            name="undeploy",
            k8s_resource=resource,
            action="delete"
        )

    kfp_client().create_run_from_pipeline_func(
        undeploy,
        {},
        run_name="undeploy",
        namespace=KF_PIPELINES_NAMESPACE
    )


def get_dataset(operators):
    """
    Find the special parameter "dataset" (which is copied to all operators)
    The prefix /tmp/data/ is added to the parameter so the operator
    receives the full path to the dataset file during a run.

    Parameters
    ----------
    operators : list

    Returns
    -------
    str
    """
    dataset = None
    for operator in operators:
        for name, value in operator.parameters.items():
            if name == "dataset":
                dataset = f"/tmp/data/{value}"
                break

    return dataset


def mount_volume_from_experiment(sdep_resource, experiment_id):
    """
    Adds volume mounts to seldon deployment k8s resource.

    Parameters
    ----------
    sdep_resource : dict
    experiment_id : str

    Returns
    -------
    dict
    """
    if volume_exists(f"vol-tmp-data-{experiment_id}", KF_PIPELINES_NAMESPACE):
        for predictor in sdep_resource["spec"]["predictors"]:
            for spec in predictor["componentSpecs"]:
                spec["spec"]["containers"][0]["volumeMounts"].append({
                    "name": "data",
                    "mountPath": "/tmp/data",
                })
                spec["spec"]["volumes"].append({
                    "name": "data",
                    "persistentVolumeClaim": {
                        "claimName": f"vol-tmp-data-{experiment_id}",
                    },
                })
    return sdep_resource


def get_task_parameter(task_parameters, name):
    """
    Get task parameter.

    Parameters
    ----------
    task_parameters : list
    name : str

    Returns
    -------
    dict
    """
    for param in task_parameters:
        param_name = param.get('name')
        if param_name == name:
            return param
