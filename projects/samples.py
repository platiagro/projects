# -*- coding: utf-8 -*-
from json import load

from .controllers.components import create_component, list_components


def init_components(config_path):
    """Installs the components from a config file. Avoids duplicates.

    Args:
        config_path (str): the path to the config file.
    """
    with open(config_path) as f:
        components = load(f)
        existing = [c["name"] for c in list_components() if c["isDefault"]]
        for component in components:
            name = component["name"]
            # if this component already exists,
            # skip this and avoid creating a duplicate
            if name in existing:
                continue
            description = component["description"]
            tags = component["tags"]
            training_notebook = read_notebook(component["trainingNotebook"])
            inference_notebook = read_notebook(component["inferenceNotebook"])
            create_component(name=name,
                             description=description,
                             tags=tags,
                             training_notebook=training_notebook,
                             inference_notebook=inference_notebook,
                             is_default=True)


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
