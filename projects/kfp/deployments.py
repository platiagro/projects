# -*- coding: utf-8 -*-
"""
Utility functions that start deployment pipelines.
"""
import json
import os
import pkgutil
from collections import defaultdict
from datetime import datetime

import yaml
from jinja2 import Template
from kfp import dsl
from kfp.components import load_component_from_text
from kfp.dsl._resource_op import kubernetes_resource_delete_op

from projects import __version__, models
from projects.kfp import kfp_client
from projects.kfp.volume import create_volume_op

DATA_VOLUME_MOUNT_PATH = "/tmp/data"
TASK_VOLUME_MOUNT_PATH = "/home/jovyan"
DEFAULT_TIMEOUT_IN_SECONDS = int(os.getenv("DEFAULT_TIMEOUT_IN_SECONDS", "600"))

DEPLOYMENT_CONTAINER_IMAGE = os.getenv(
    "DEPLOYMENT_CONTAINER_IMAGE",
    f"platiagro/platiagro-deployment-image:{__version__}",
)
TASK_NVIDIA_VISIBLE_DEVICES = os.getenv("TASK_NVIDIA_VISIBLE_DEVICES", "none")
SELDON_REST_TIMEOUT = os.getenv("SELDON_REST_TIMEOUT", "60000")

SELDON_LOGGER_ENDPOINT = os.getenv("SELDON_LOGGER_ENDPOINT", "http://projects.platiagro:8080")
SELDON_DEPLOYMENT = Template(pkgutil.get_data("projects", "kfp/resources/SeldonDeployment.yaml").decode())
COMPONENT_SPEC = Template(pkgutil.get_data("projects", "kfp/resources/SeldonPodSpec.yaml").decode())
PREDICTIVE_UNIT = Template(pkgutil.get_data("projects", "kfp/resources/PredictiveUnit.yaml").decode())


def run_deployment(deployment: models.Deployment, namespace: str):
    """
    Starts a Kubeflow Pipeline that creates K8s resources necessary for deployments.

    Creates:
    - A container that runs the Deployment.ipynb notebook of a task.
    - A SeldonDeployment that serves a REST API using a class defined in Model.py.

    Parameters
    ----------
    deployment : model.Deployment
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Create Deployment",
        description="A pipeline that creates all resources necessary for a new deployment.",
    )
    def pipeline_func():
        # Creates a volume shared amongst all containers in this pipeline
        volume_op_tmp_data = create_volume_op(name=f"tmp-data-{deployment.uuid}", namespace=namespace)

        # Uses a dict to map operator.uuid -> (ContainerOp, Operator)
        kfp_ops = {}

        for operator in deployment.operators:
            # Creates one ContainerOp instance for each Operator
            container_op = create_container_op_from_operator(operator=operator)

            # adds shared volume to the container
            container_op.add_pvolumes({DATA_VOLUME_MOUNT_PATH: volume_op_tmp_data.volume})

            # adds task volume to the container
            volume_op_home_jovyan = create_volume_op(name=f"task-{operator.task_id}", namespace=namespace)
            container_op.add_pvolumes({TASK_VOLUME_MOUNT_PATH: volume_op_home_jovyan.volume})

            kfp_ops[operator.uuid] = (operator, container_op)

        # Creates a SeldonDeployment
        seldon_deployment_op = create_seldon_deployment_op(deployment=deployment, namespace=namespace)

        for operator, container_op in kfp_ops.values():
            # Sets their dependencies using the mapping
            dependencies = [kfp_ops[dependency_id][1] for dependency_id in operator.dependencies]
            container_op.after(*dependencies)

            seldon_deployment_op.after(container_op)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{deployment.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=deployment.uuid,
        namespace=namespace,
    )


def delete_deployment(deployment: models.Deployment, namespace: str):
    """
    Runs a Kubeflow Pipeline that deletes seldon deployment.

    Parameters
    ----------
    deployment : models.Deployment
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Delete Deployment",
        description="A pipeline that deletes K8s resources associated with a given deployment.",
    )
    def pipeline_func():
        delete_seldon_deployment_op(deployment=deployment, namespace=namespace)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{deployment.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=deployment.uuid,
    )


def create_container_op_from_operator(operator: models.Operator):
    """
    Creates a kfp.ContainerOp using data from an Operator.

    Parameters
    ----------
    operator : models.Operator

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    name = operator.name
    image = operator.task.image
    command = operator.task.commands
    args = operator.task.arguments
    component = {
        "name": name,
        "description": "",

        "inputs": [],

        "outputs": [],

        "implementation": {
            "container": {
                "image": image,
                "command": command,
                "args": args,
                "env": {},
            },
        },
    }
    text = json.dumps(component)
    func = load_component_from_text(text)
    return func()


def create_seldon_deployment_op(deployment: models.Deployment, namespace: str):
    """
    Creates a kfp.ResourceOp using data from a deployment.

    Parameters
    ----------
    deployment : models.Deployment
    namespace : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    component_specs = []

    # Removes operators that can't be part of a seldondeployment (eg. Upload de Dados).
    # Also, fix dependencies.
    deployable_operators = select_deployable_operators(deployment.operators)

    for operator in deployable_operators:
        spec = COMPONENT_SPEC.render(
            image=DEPLOYMENT_CONTAINER_IMAGE,
            operator_id=operator.uuid,
            experiment_id=deployment.experiment_id,
            deployment_id=deployment.uuid,
            task_id=operator.task.uuid,
            memory_limit=operator.task.memory_limit,
            memory_request=operator.task.memory_request,
            task_name=operator.task.name,
            nvidia_visible_devices=TASK_NVIDIA_VISIBLE_DEVICES,
        )

        component_specs.append(spec)

    first = None
    graph = defaultdict(list)
    for operator in deployable_operators:
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
            children = "[]"

        return PREDICTIVE_UNIT.render(
            name=operator_id,
            children=children,
        )

    graph = build_graph(operator_id=first, children=graph[first])
    graph = yaml.load(graph)

    url = f"{SELDON_LOGGER_ENDPOINT}/projects/{deployment.project_id}/deployments/{deployment.uuid}/responses"
    graph["logger"] = {
        "mode": "response",
        "url": url,
    }

    seldon_deployment = SELDON_DEPLOYMENT.render(
        namespace=namespace,
        deployment_id=deployment.uuid,
        component_specs=component_specs,
        graph=graph,
        project_id=deployment.project_id,
        rest_timeout=SELDON_REST_TIMEOUT,
    )

    sdep_resource = yaml.load(seldon_deployment)

    # mounts the "/tmp/data" volume from experiment (if exists)
    # TODO sdep_resource = mount_volume_from_experiment(sdep_resource, experiment_id)

    resource_op = dsl.ResourceOp(
        name="deployment",
        k8s_resource=sdep_resource,
        success_condition="status.state == Available",
        attribute_outputs={
            "name": "{.metadata.name}",
            "created_at": datetime.utcnow().isoformat(),
        },
    ).set_timeout(DEFAULT_TIMEOUT_IN_SECONDS)

    # attribute_outputs makes this ResourceOp to have a unique cache key
    # Each op is cached based on a key formed by:
    # container, inputs, outputs, volumes, initContainers and sidecars
    # See: https://github.com/kubeflow/pipelines/blob/cc83e1089b573256e781ed2e4ac90f604129e769/backend/src/cache/server/mutation.go#L232-L245

    # If the keys are repeated, then the workflow will not run for a second time.
    # This caused issues for ResourceOps where the cache keys were the same for all resources.
    # (only the resource yaml changes; container, inputs, outputs, volumes, initContainers and sidecars were the same).

    return resource_op


def delete_seldon_deployment_op(deployment: models.Deployment, namespace: str):
    """
    Creates a kfp.dsl.ContainerOp that deletes a volume (Kubernetes Resource).

    Parameters
    ----------
    deployment : models.Deployment
    namespace : str

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    kind = "seldondeployments.machinelearning.seldon.io"
    return kubernetes_resource_delete_op(
        name=deployment.name,
        kind=kind,
        namespace=namespace,
    )


def select_deployable_operators(operators):
    """
    Removes operators that can't be part of a deployment pipeline and fix dependencies.

    Parameters
    ----------
    operators : list
        Original pipeline operators.

    Returns
    -------
    list
        A list of all deployable operators.

    Notes
    -----
    If a non-deployable operator is dependent on another operator, it will be
    removed from that operator's dependency list.
    """
    deployable_operators = [o for o in operators if o.task.deployment_notebook_path is not None]
    non_deployable_operators = get_non_deployable_operators(operators, deployable_operators)

    for operator in deployable_operators:
        dependencies = set(operator.dependencies)
        operator.dependencies = list(dependencies - set(non_deployable_operators))

    return deployable_operators


def get_non_deployable_operators(operators, deployable_operators):
    """
    Get all non-deployable operators from a deployment run.

    Parameters
    ----------
    operators : list
    deployable_operators : list

    Returns
    -------
    list
        A list of non deployable operators.
    """
    non_deployable_operators = []
    for operator in operators:
        if operator.task.deployment_notebook_path is None:
            # checks if the non-deployable operator has dependency
            if operator.dependencies:
                dependency = operator.dependencies

                # looks for who has the non-deployable operator as dependency
                # and assign the dependency of the non-deployable operator to this operator
                for op in deployable_operators:
                    if operator.uuid in op.dependencies:
                        op.dependencies = dependency

            non_deployable_operators.append(operator.uuid)

    return non_deployable_operators
