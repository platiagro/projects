# -*- coding: utf-8 -*-
"""Metrics blueprint."""

from flask import Blueprint, jsonify

from ..controllers.metrics import list_metrics

bp = Blueprint("metrics", __name__)


@bp.route("", methods=["GET"])
def handle_list_metrics(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    metrics = list_metrics(experiment_id=experiment_id,
                           operator_id=operator_id,
                           run_id='latest')
    return jsonify(metrics)


@bp.route("<run_id>", methods=["GET"])
def handle_list_metrics_by_run_id(project_id, experiment_id, operator_id, run_id):
    """Handles GET requests to /<run_id>."""
    metrics = list_metrics(experiment_id=experiment_id,
                           operator_id=operator_id,
                           run_id=run_id)
    return jsonify(metrics)
