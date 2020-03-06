# -*- coding: utf-8 -*-
from json import load

from .controllers.components import create_component


def init_components(config_path):
    """Installs the components from a config file.

    Args:
        config_path (str): the path to the config file.
    """
    with open(config_path) as f:
        components = load(f)
        for component in components:
            name = component["name"]
            training_notebook = component["trainingNotebook"]
            inference_notebook = component["inferenceNotebook"]
            create_component(name=name,
                             training_notebook=training_notebook,
                             inference_notebook=inference_notebook,
                             is_default=True)
