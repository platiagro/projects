# -*- coding: utf-8 -*-
"""
Utility functions that start email pipelines.
"""
import json
import os

from kfp import dsl
from kfp.components import load_component_from_text

from projects import __version__, models
from projects.kfp import kfp_client
from projects.kfp.volume import create_volume_op

TASK_VOLUME_MOUNT_PATH = "/home/jovyan"
SHARE_TASK_CONTAINER_IMAGE = os.getenv(
    "INIT_TASK_CONTAINER_IMAGE",
    f"platiagro/share-task:{__version__}-SNAPSHOT",
)
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_SENDER_ADDRESS = os.getenv("MAIL_SENDER_ADDRESS", "")
MAIL_SERVER = os.getenv("MAIL_SERVER", "")
MAIL_PORT = str(os.getenv("MAIL_PORT", 587))
MAIL_TLS = str(os.getenv("MAIL_TLS", True))
MAIL_SSL = str(os.getenv("MAIL_SSL", False))


def send_email(task: models.Task, namespace: str):
    """
    Runs a Kubeflow Pipeline that sends an email with task contents as an attachment.

    Parameters
    ----------
    task : models.Task
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Share Task",
        description="A pipeline that sends an email with the contents of a task attached.",
    )
    def pipeline_func():
        """
        Defines a Kubeflow Pipeline using Task details.
        """
        # Creates a volume for this task
        volume_op_task = create_volume_op(name=f"task-{task.name}", namespace=namespace)

        # Creates one ContainerOp to copy task contents
        image = SHARE_TASK_CONTAINER_IMAGE
        component = {
            "name": "share-task",
            "description": "",

            "inputs": [],

            "outputs": [],

            "implementation": {
                "container": {
                    "image": image,
                    "env": {
                        "MAIL_USERNAME": MAIL_USERNAME,
                        "MAIL_PASSWORD": MAIL_PASSWORD,
                        "MAIL_FROM": MAIL_SENDER_ADDRESS,
                        "MAIL_PORT": MAIL_PORT,
                        "MAIL_SERVER": MAIL_SERVER,
                        "MAIL_TLS": MAIL_TLS,
                        "MAIL_SSL": MAIL_SSL,
                    },
                },
            },
        }
        text = json.dumps(component)
        func = load_component_from_text(text)
        container_op = func()
        container_op.add_pvolumes({TASK_VOLUME_MOUNT_PATH: volume_op_task.volume})

    run_name = f"Share Task - {task.name}"

    return kfp_client(namespace).create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=task.uuid,
        namespace=namespace,
    )
