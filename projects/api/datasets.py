# -*- coding: utf-8 -*-
"""Datasets blueprint."""

from flask_smorest import Blueprint

from ..controllers.datasets import get_dataset, get_dataset_pagination

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
def handle_get_dataset(project_id, experiment_id, operator_id):
    """Handles GET requests to /."""
    return get_dataset(project_id=project_id, experiment_id=experiment_id, operator_id=operator_id)


@bp.route("/", methods=["GET"])
@bp.paginate()
def handle_get_dataset_paginated(project_id, experiment_id, operator_id, pagination_parameters):
    """Handles GET requests to /."""
    datasets = get_dataset_pagination(project_id=project_id, experiment_id=experiment_id, operator_id=operator_id,
                                      page=pagination_parameters.page, page_size=pagination_parameters.page_size)
    return datasets
