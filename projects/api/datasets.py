# -*- coding: utf-8 -*-
"""Datasets blueprint."""

from flask_smorest import Blueprint

from ..controllers.datasets import get_dataset_pagination

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
@bp.paginate()
def handle_list_datasets(project_id, experiment_id, operator_id, pagination_parameters):
    """Handles GET requests to /."""
    pagination_parameters.item_count = 0
    datasets = get_dataset_pagination(project_id=project_id,
                                      experiment_id=experiment_id,
                                      operator_id=operator_id,
                                      page=pagination_parameters.page,
                                      page_size=pagination_parameters.page_size,
                                      run_id='latest')

    return datasets


@bp.route("<run_id>", methods=["GET"])
@bp.paginate()
def handle_list_datasets_by_run_id(project_id,
                                   experiment_id,
                                   operator_id,
                                   pagination_parameters,
                                   run_id):
    """Handles GET requests to /<run_id>."""
    pagination_parameters.item_count = 0
    datasets = get_dataset_pagination(project_id=project_id,
                                      experiment_id=experiment_id,
                                      operator_id=operator_id,
                                      page=pagination_parameters.page,
                                      page_size=pagination_parameters.page_size,
                                      run_id=run_id)

    return datasets
