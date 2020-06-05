# -*- coding: utf-8 -*-
"""Metrics blueprint."""

from flask import Blueprint, jsonify

from ..controllers.metrics import list_metrics

bp = Blueprint("metrics", __name__)


@bp.route("", methods=["GET"])
def handle_list_metrics(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    return jsonify(list_metrics(project_id=project_id,
                                experiment_id=experiment_id,
                                operator_id=operator_id))
