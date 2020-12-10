# -*- coding: utf-8 -*-
"""Experiment Logs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers.experiments.runs.logs import get_logs

bp = Blueprint("experiment_logs", __name__)


@bp.route("", methods=["GET"])
def handle_list_logs(project_id, experiment_id, run_id, operator_id):
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
    logs = get_logs(project_id=project_id,
                    experiment_id=experiment_id,
                    run_id=run_id,
                    operator_id=operator_id)

    return jsonify(logs)
