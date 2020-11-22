# -*- coding: utf-8 -*-
"""Experiment Metrics blueprint."""
from flask import Blueprint, jsonify

from projects.controllers.experiments.runs.metrics import list_metrics

bp = Blueprint("metrics", __name__)


@bp.route("", methods=["GET"])
def handle_list_metrics(project_id, experiment_id, run_id, operator_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    operator_id : str

    Returns
    -------
    str
    """
    metrics = list_metrics(project_id=project_id,
                           experiment_id=experiment_id,
                           operator_id=operator_id,
                           run_id=run_id)
    return jsonify(metrics)
