# -*- coding: utf-8 -*-
"""Logs blueprint."""

from flask import Blueprint, jsonify

from ..jupyter import get_notebook_output

bp = Blueprint("logs", __name__)


@bp.route("", methods=["GET"])
def handle_notebook_logs(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    logs = get_notebook_output(experiment_id=experiment_id,
                               operator_id=operator_id)

    return jsonify(logs)
