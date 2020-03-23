# -*- coding: utf-8 -*-
"""Parameters controller."""

from werkzeug.exceptions import NotFound

from ..models import Component
from ..jupyter import read_parameters


def list_parameters(component_id, is_checked=False):
    """Lists all parameters from the training notebook of a component.

    Args:
        component_id (str): the component uuid to look for in our database.

    Returns:
        A list of all parameters.
    """
    component = Component.query.get(component_id)
    if component is None:
        raise NotFound("The specified component does not exist")

    return read_parameters(component.training_notebook_path)
