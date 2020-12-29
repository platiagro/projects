# -*- coding: utf-8 -*-
import json
import os

import requests
from werkzeug.exceptions import BadRequest

from projects.controllers.tasks import create_task
from projects.models.task import DEFAULT_IMAGE
from projects.object_storage import put_object


def init_tasks(config_path):
    """
    Creates tasks from a config file. Avoids duplicates.

    Parameters
    ----------
    config_path : str
        The path to the config file.
    """
    with open(config_path) as f:
        tasks = load(f)

        for task in tasks:
            name = task["name"]
            description = task.get("description")
            tags = task.get("tags", ["DEFAULT"])

            default_image = os.environ.get("PLATIAGRO_NOTEBOOK_IMAGE", DEFAULT_IMAGE)
            image = task.get("image", default_image)

            commands = task.get("commands")
            arguments = task.get("arguments")

            try:
                experiment_notebook = read_notebook(task["experimentNotebook"])
            except KeyError:
                experiment_notebook = None

            try:
                deployment_notebook = read_notebook(task["deploymentNotebook"])
            except KeyError:
                deployment_notebook = None

            try:
                create_task(name=name,
                            description=description,
                            tags=tags,
                            image=image,
                            commands=commands,
                            arguments=arguments,
                            experiment_notebook=experiment_notebook,
                            deployment_notebook=deployment_notebook,
                            is_default=True)
            except BadRequest:
                pass


def read_notebook(notebook_path):
    """
    Reads the contents of a notebook file.

    Parameters
    ----------
    notebook_path :str
        The path to the notebook file.

    Returns
    -------
    bytes
        The notebook content as bytes.
    """
    with open(notebook_path, "rb") as f:
        notebook = json.load(f)
    return notebook


def init_artifacts(config_path):
    """
    Copies the artifacts from a config file to MinIO.

    Parameters
    ----------
    config_path : str
        The path to the config file.
    """
    with open(config_path) as f:
        artifacts = json.load(f)

    for artifact in artifacts:
        file_path = artifact["file_path"]
        object_name = artifact["object_name"]

        with open(file_path, "rb") as f:
            put_object(object_name, f.read())
