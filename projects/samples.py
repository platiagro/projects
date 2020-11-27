# -*- coding: utf-8 -*-
from json import load

from os import environ

from projects.controllers.tasks import create_task

from projects import __version__

from werkzeug.exceptions import BadRequest


def init_tasks(config_path, default_image=None):
    """Installs the tasks from a config file. Avoids duplicates.

    Args:
        config_path (str): the path to the config file.
        default_image (str): the default image to be used on a task.
    """
    if not default_image:
        default_image = f"platiagro/platiagro-notebook-image:{__version__}"

    with open(config_path) as f:
        tasks = load(f)

        for task in tasks:
            name = task["name"]
            description = task["description"]
            tags = task["tags"]

            if "image" in task:
                image = task["image"]
            else:
                image = environ.get("PLATIAGRO_NOTEBOOK_IMAGE", default_image)

            commands = task["commands"]
            arguments = task["arguments"]

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
    """Reads the contents of a notebook.

    Args:
        notebook_path (str): the path to the notebook file.

    Returns:
        The notebook content as bytes.
    """
    with open(notebook_path, "rb") as f:
        notebook = load(f)
    return notebook
