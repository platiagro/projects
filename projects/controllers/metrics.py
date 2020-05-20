# -*- coding: utf-8 -*-
"""Metrics controller."""

import platiagro

from werkzeug.exceptions import NotFound


def list_metrics(project_id, experiment_id):
    """Lists all metrics from object storage.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.

    Returns:
        A list of metrics.
    """
    try:
        return platiagro.list_metrics(experiment_id=experiment_id)
    except FileNotFoundError as e:
        raise NotFound(str(e))
