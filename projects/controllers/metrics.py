# -*- coding: utf-8 -*-
"""Metrics controller."""

import platiagro

from werkzeug.exceptions import NotFound


def list_metrics(experiment_id, operator_id, run_id):
    """Lists all metrics from object storage.
    Args:
        experiment_id (str): the experiment uuid.
        operator_id (str): the operator uuid.
        run_id (str): the run id.
    Returns:
        A list of metrics.
    """
    try:
        return platiagro.list_metrics(experiment_id=experiment_id,
                                      operator_id=operator_id,
                                      run_id=run_id)
    except FileNotFoundError as e:
        raise NotFound(str(e))
