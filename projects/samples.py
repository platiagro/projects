# -*- coding: utf-8 -*-
from json import load

from werkzeug.exceptions import BadRequest

from .controllers.components import create_component


def init_components(config_path):
    """Installs the components from a config file. Avoids duplicates.

    Args:
        config_path (str): the path to the config file.
    """
    with open(config_path) as f:
        components = load(f)

        for component in components:
            name = component["name"]
            description = component["description"]
            tags = component["tags"]

            try:
                component_id = component["uuid"]
            except KeyError:
                component_id = None

            try:
                experiment_notebook = read_notebook(component["experimentNotebook"])
            except KeyError:
                experiment_notebook = None

            try:
                deployment_notebook = read_notebook(component["deploymentNotebook"])
            except KeyError:
                deployment_notebook = None

            try:
                create_component(component_id=component_id,
                                 name=name,
                                 description=description,
                                 tags=tags,
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
