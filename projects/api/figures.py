# -*- coding: utf-8 -*-
"""Figures blueprint."""

from flask import Blueprint, jsonify

from ..controllers.figures import list_figures

bp = Blueprint("figures", __name__)


@bp.route("", methods=["GET"])
def handle_list_figures(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    return jsonify(list_figures(experiment_id=experiment_id,
                                operator_id=operator_id))
