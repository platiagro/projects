# -*- coding: utf-8 -*-
"""
Utility functions that start task pipelines.
"""
import json
import os
import pkgutil
from datetime import datetime
from typing import Dict, List, Optional

from jinja2 import Template
from kfp import dsl
from kfp.components import load_component_from_text

from projects import __version__, models
from projects.kfp import kfp_client
from projects.kfp.volume import create_volume_op, delete_volume_op

TASK_VOLUME_MOUNT_PATH = "/home/jovyan/tasks"
SOURCE_TASK_VOLUME_MOUNT_PATH = "/home/source"
DESTINATION_TASK_VOLUME_MOUNT_PATH = "/home/destination"
DEFAULT_TIMEOUT_IN_SECONDS = 120

INIT_TASK_CONTAINER_IMAGE = os.getenv(
    "INIT_TASK_CONTAINER_IMAGE",
    f"platiagro/init-task:{__version__}-SNAPSHOT",
)
TASK_CONFIGMAP = Template(pkgutil.get_data("projects", "kfp/resources/TaskConfigMap.yaml").decode())


def create_task(task: models.Task, all_tasks: List[models.Task], namespace: str, copy_from: Optional[models.Task] = None):
    """
    Runs a Kubeflow Pipeline that creates all resources necessary for a new task.

    Creates a persistent volume, copies files into the volume, and patches
    notebook server (updates volumes and volumeMounts).

    Parameters
    ----------
    task : models.Task
    all_tasks : List[models.Task]
    namespace : str
    copy_from : models.Task or None

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Create Task",
        description="A pipeline that creates all resources necessary for a new task.",
    )
    def pipeline_func():
        # Creates a volume for this task
        volume_op_task = create_volume_op(name=f"task-{task.uuid}", namespace=namespace)

        # And a ContainerOp to initialize task contents
        # Either the contents of other task are copied,
        # or some empty notebooks are copied into the volume
        container_op = create_init_task_container_op(task=task, copy_from=copy_from)
        container_op.add_pvolumes({DESTINATION_TASK_VOLUME_MOUNT_PATH: volume_op_task.volume})
        container_op.set_timeout(DEFAULT_TIMEOUT_IN_SECONDS)

        if copy_from:
            # If task is a copy, also adds a volume mount to the source task volume
            volume_op_task = create_volume_op(name=f"task-{copy_from.uuid}", namespace=namespace)
            container_op.add_pvolumes({SOURCE_TASK_VOLUME_MOUNT_PATH: volume_op_task.volume})

        if task.category == "MONITORING":
            # if it is a "MONITORING task", creates a configmap using the contents of this task.
            # knative serving (monitoring service) does not support stateful resources like
            # persistentvolumes, so we have to use a configmap to create a volumeMount into
            # the monitoring service.
            # TODO add real task content
            create_configmap_op(task=task, namespace=namespace, content="")

        # Patches JupyterLab to mount new task volume
        patch_notebook_volume_mounts_op(tasks=all_tasks, namespace=namespace).after(container_op)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{task.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=task.uuid,
        namespace=namespace,
    )


def update_task(
        task: models.Task,
        all_tasks: List[models.Task],
        namespace: str,
        experiment_notebook: Optional[Dict],
        deployment_notebook: Optional[Dict],
):
    """
    Runs a Kubeflow Pipeline that .

    Parameters
    ----------
    task : models.Task
    all_tasks : List[models.Task]
    namespace : str
    experiment_notebook : Dict or None
    deployment_notebook : Dict or None

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Update Task",
        description="A pipeline that updates K8s resources with updated attributes of a given task.",
    )
    def pipeline_func():

        # if the contents of a notebook are sent, the files on task volume must be updated
        if experiment_notebook or deployment_notebook:
            volume_op_task = create_volume_op(name=f"task-{task.uuid}", namespace=namespace)
            container_op = create_init_task_container_op(task=task)
            container_op.add_pvolumes({DESTINATION_TASK_VOLUME_MOUNT_PATH: volume_op_task.volume})

        patch_notebook_volume_mounts_op(tasks=all_tasks, namespace=namespace)
        if task.category == "MONITORING":
            # Updates ConfigMap if category is MONITORING
            # TODO add real task content
            create_configmap_op(task=task, namespace=namespace, content="")

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{task.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=task.uuid,
        namespace=namespace,
    )


def delete_task(task: models.Task, all_tasks: List[models.Task], namespace: str):
    """
    Runs a Kubeflow Pipeline that deletes the volume of a task and removes it from JupyterLab.

    Parameters
    ----------
    task : models.Task
    all_tasks : List[models.Task]
    namespace : str

    Returns
    -------
    RunPipelineResult
    """

    @dsl.pipeline(
        name="Delete Task",
        description="A pipeline that deletes K8s resources associated with a given task.",
    )
    def pipeline_func():
        # Patches JupyterLab to remove volumeMount
        resource_op = patch_notebook_volume_mounts_op(tasks=all_tasks, namespace=namespace)

        delete_volume_op(name=f"task-{task.uuid}", namespace=namespace).after(resource_op)

    tag = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
    run_name = f"{task.name}-{tag}"

    return kfp_client().create_run_from_pipeline_func(
        pipeline_func=pipeline_func,
        arguments={},
        run_name=run_name,
        experiment_name=task.uuid,
    )


def create_init_task_container_op(
    task: models.Task,
    copy_from: Optional[models.Task] = None,
    experiment_notebook: Optional[Dict] = None,
    deployment_notebook: Optional[Dict] = None,
):
    """
    Creates a kfp.ContainerOp that initializes a task.

    Either copies the contents of another task, or copies the "empty" Jupyter Notebooks.

    Parameters
    ----------
    task : model.Task
    copy_from : model.Task or None
    experiment_notebook : Dict or None
    deployment_notebook : Dict or None

    Returns
    -------
    kfp.dsl.ContainerOp
    """
    args = ["--task-id", task.uuid, "--destination", DESTINATION_TASK_VOLUME_MOUNT_PATH]

    if copy_from:
        args.extend(["--source", SOURCE_TASK_VOLUME_MOUNT_PATH])

    if experiment_notebook:
        # BUG
        # If len(experiment_notebook) is greater that OS limit, it will truncate
        # See this URL https://serverfault.com/questions/163371/linux-command-line-character-limit
        # for further details
        args.extend(["--experiment-notebook", experiment_notebook])

    if deployment_notebook:
        # BUG
        # Same problem described for experiment_notebook.
        args.extend(["--deployment-notebook", deployment_notebook])

    component = {
        "name": "init-task",
        "description": "",

        "inputs": [],

        "outputs": [],

        "implementation": {
            "container": {
                "image": INIT_TASK_CONTAINER_IMAGE,
                "args": args,
            },
        },
    }
    text = json.dumps(component)
    func = load_component_from_text(text)
    return func()


def patch_notebook_volume_mounts_op(tasks: List[models.Task], namespace: str):
    """
    Creates a kfp.ResourceOp that patches notebook server.

    Sets volumes and a volumeMounts for all tasks.

    Parameters
    ----------
    tasks : List[models.Task]
    namespace : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    k8s_resource = {
        "apiVersion": "kubeflow.org/v1",
        "kind": "Notebook",
        "metadata": {
            "name": "server",
            "namespace": namespace,
            "labels": {
                "app": "server"
            }
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "server",
                            "image": "platiagro/platiagro-notebook-image:0.3.0",
                            "env": [
                                {
                                    "name": "EXPERIMENT_ID",
                                    "value": "notebook"
                                },
                                {
                                    "name": "OPERATOR_ID",
                                    "value": "notebook"
                                },
                                {
                                    "name": "MINIO_ENDPOINT",
                                    "value": "minio.platiagro:9000"
                                },
                                {
                                    "name": "MINIO_ACCESS_KEY",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "key": "MINIO_ACCESS_KEY",
                                            "name": "minio-secrets"
                                        }
                                    }
                                },
                                {
                                    "name": "MINIO_SECRET_KEY",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "key": "MINIO_SECRET_KEY",
                                            "name": "minio-secrets"
                                        }
                                    }
                                }
                            ],
                            "volumeMounts": [
                                {
                                    "mountPath": "/home/jovyan/tasks",
                                    "name": "vol-tasks"
                                },
                                {
                                    "mountPath": "/home/jovyan/experiments",
                                    "name": "vol-experiments"
                                },
                                {
                                    "mountPath": "/tmp/data",
                                    "name": "vol-datasets"
                                }
                            ]
                        }
                    ],
                    "serviceAccountName": "default-editor",
                    "ttlSecondsAfterFinished": 300,
                    "volumes": [
                        {
                            "name": "vol-tasks",
                            "persistentVolumeClaim": {
                                "claimName": "vol-tasks"
                            }
                        },
                        {
                            "name": "vol-experiments",
                            "persistentVolumeClaim": {
                                "claimName": "vol-experiments"
                            }
                        },
                        {
                            "name": "vol-datasets",
                            "persistentVolumeClaim": {
                                "claimName": "vol-datasets"
                            }
                        }
                    ]
                }
            }
        }
    }

    for task in tasks:
        name = f"vol-task-{task.uuid}"
        mount_path = f"{TASK_VOLUME_MOUNT_PATH}/{task.name}"

        k8s_resource["spec"]["template"]["spec"]["volumes"].append(
            {
                "name": name,
                "persistentVolumeClaim": {
                    "claimName": name,
                },
            }
        )

        k8s_resource["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
            {
                "mountPath": mount_path,
                "name": name,
            }
        )

    return dsl.ResourceOp(
        name="patch-notebook",
        k8s_resource=k8s_resource,
        action="apply",
        attribute_outputs={
            "name": "{.metadata.name}",
            "created_at": datetime.utcnow().isoformat(),
        },  # makes this ResourceOp to have a unique cache key
    )


def create_configmap_op(task: models.Task, namespace: str, content: str):
    """
    Creates a kfp.ResourceOp that creates a configmap for task.

    Parameters
    ----------
    task : models.Task
    namespace : str
    content : str

    Returns
    -------
    kfp.dsl.ResourceOp
    """
    k8s_resource = TASK_CONFIGMAP.render(
        name=f"configmap-{task.uuid}",
        namespace=namespace,
        content=content,
    )

    return dsl.ResourceOp(
        name=task.name,
        k8s_resource=k8s_resource,
        action="apply",
        attribute_outputs={
            "name": "{.metadata.name}",
            "created_at": datetime.utcnow().isoformat(),
        },  # makes this ResourceOp to have a unique cache key
    )
