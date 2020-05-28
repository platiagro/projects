# -*- coding: utf-8 -*-
"""Datasets blueprint."""

from flask import Blueprint

from ..controllers.datasets import get_dataset

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
def handle_get_dataset(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    return get_dataset(project_id=project_id, experiment_id=experiment_id, operator_id=operator_id)
