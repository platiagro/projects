# -*- coding: utf-8 -*-
"""Logs controller."""

from ..jupyter import get_notebook_output

from werkzeug.exceptions import NotFound


def get_logs(experiment_id, operator_id):
    """Get notebook logs.

    Args:
        experiment_id (str): experiment id
        operator_id (str): operator id

    Raises:
        NotFound: Notebook does not exist

    Returns:
        dict: a dict of output.
    """
    try:
        return get_notebook_output(experiment_id, operator_id)
    except FileNotFoundError as e:
        raise NotFound(str(e))
