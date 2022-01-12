# -*- coding: utf-8 -*-
"""
Utility functions that start email pipelines.
"""
import json
import os
from datetime import datetime
from urllib3.exceptions import MaxRetryError

from kfp import dsl
from kfp.components import load_component_from_text
from projects import __version__, models
from projects.kfp import kfp_client
from projects.kfp.volume import create_volume_op
from projects.exceptions import ServiceUnavailable, Forbidden, NotFound

from kfp_server_api.exceptions import ApiException
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


def send_email(task: models.Task, namespace: str, email_schema):
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
        volume_op_task = create_volume_op(name=f"task-{task.uuid}", namespace=namespace)

        # Creates one ContainerOp to copy task contents
        image = SHARE_TASK_CONTAINER_IMAGE
        now = datetime.utcnow().isoformat()
        command = [
            "python", "-m", "projects.share_task.main",
            "--source", {"inputValue": "source"},
            "--emails", {"inputValue": "emails"},
            "--task-name", {"inputValue": "task-name"},
            "--requested-at", {"inputValue": "requested-at"}
        ]

        component = {
            "name": f"share-task-{now}",
            "description": "",
            "outputs": [],
            "inputs": [
                {"name": "source", "description": "Mountpath of volume"},
                {"name": "emails", "description": "Email list"},
                {"name": "task-name", "description": "Task name"},
                {"name": "requested-at", "description": "Time of request"},
            ],

            "implementation": {
                "container": {
                    "image": image,
                    "env": {
                        "MAIL_USERNAME": MAIL_USERNAME,
                        "MAIL_PASSWORD": MAIL_PASSWORD,
                        "MAIL_SENDER_ADDRESS": MAIL_SENDER_ADDRESS,
                        "MAIL_PORT": MAIL_PORT,
                        "MAIL_SERVER": MAIL_SERVER,
                        "MAIL_TLS": MAIL_TLS,
                        "MAIL_SSL": MAIL_SSL,
                    },
                    "command": command,


                },
            },
        }
        text = json.dumps(component)
        email_list_str = " ".join(email for email in email_schema.emails)

        func = load_component_from_text(text)
        mount_path = TASK_VOLUME_MOUNT_PATH
        container_op = func(mount_path, email_list_str, task.name, now)
        container_op.add_pvolumes({TASK_VOLUME_MOUNT_PATH: volume_op_task.volume})

    run_name = f"Share Task - {task.name}"
    try:
        return kfp_client().create_run_from_pipeline_func(
            pipeline_func=pipeline_func,
            arguments={},
            run_name=run_name,
            experiment_name=task.uuid,
            namespace=namespace,
            enable_caching=False
        )
    except ApiException as e:
        # Happens when there's no health upstream for kubeflow pipelines
        if e.status == 404:
            raise NotFound(e.status, e.reason)
        if e.status == 403:
            raise Forbidden(e.status, e.reason)
        else:
            raise ServiceUnavailable(e.status, e.reason)
    except MaxRetryError as e:
        # Happens when there's no connection available for kubeflow pipelines
        raise ServiceUnavailable("NoConnectionKFP", "there's no connection available for kubeflow pipelines")
