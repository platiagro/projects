# -*- coding: utf-8 -*-
"""Deployment Logs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers.deployments.runs.logs import list_logs

bp = Blueprint("deployment_logs", __name__)


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
    logs = list_logs(project_id, experiment_id, operator_id)
    return jsonify(logs)
