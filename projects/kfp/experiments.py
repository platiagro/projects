# -*- coding: utf-8 -*-
"""
Utility functions that start experiment pipelines.
"""
import json
from datetime import datetime

from kfp import dsl
from kfp.components import load_component_from_text

from projects import models
from projects.kfp import kfp_client
from projects.kfp.volume import create_volume_op

DATA_VOLUME_MOUNT_PATH = "/tmp/data"
TASK_VOLUME_MOUNT_PATH = "/home/jovyan"

DEFAULT_TIMEOUT_IN_SECONDS = 120


def run_experiment(experiment: models.Experiment, namespace: str):
    """
    Starts a Kubeflow Pipeline that runs the operators of a experiment.

    Parameters
    ----------
    experiment : model.Experiment
    namespace : str
    """

    @dsl.pipeline(
        name="Run Experiment",
        description="A pipeline that run a series of operators/tasks associated with an experiment.",
    )
    def pipeline_func():
        # Creates a volume shared amongst all containers in this pipeline
        volume_op_tmp_data = create_volume_op(name=f"tmp-data-{experiment.uuid}", namespace=namespace)

        # Uses a dict to map operator.uuid -> (ContainerOp, Operator)
        kfp_ops = {}

        for operator in experiment.operators:
            # Creates one ContainerOp instance for each Operator
            container_op = create_container_op_from_operator(operator=operator)

            # adds shared volume to the container
            container_op.add_pvolumes({DATA_VOLUME_MOUNT_PATH: volume_op_tmp_data.volume})

            # adds task volume to the container
            volume_op_home_jovyan = create_volume_op(name=f"task-{operator.task_id}", namespace=namespace)
            container_op.add_pvolumes({TASK_VOLUME_MOUNT_PATH: volume_op_home_jovyan.volume})

            kfp_ops[operator.uuid] = (operator, container_op)

        for operator, container_op in kfp_ops.values():
            # Sets their dependencies using the mapping
            dependencies = [kfp_ops[dependency_id][1] for dependency_id in operator.dependencies]
            container_op.after(*dependencies)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{experiment.name}-{tag}"

    kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=experiment.uuid,
        namespace=namespace,
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
    image = operator.image
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
    return func().set_timeout(DEFAULT_TIMEOUT_IN_SECONDS)
