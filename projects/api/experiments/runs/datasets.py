# -*- coding: utf-8 -*-
"""Experiment Datasets blueprint."""
from flask_smorest import Blueprint

from projects.controllers.experiments.runs.datasets import list_datasets

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
@bp.paginate()
def handle_list_datasets(project_id, experiment_id, run_id, operator_id, pagination_parameters):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    operator_id : str
    pagination_parameters : flask_smorest.pagination.PaginationParameters

    Returns
    -------
    List
    """
    pagination_parameters.item_count = 0
    datasets = list_datasets(project_id=project_id,
                             experiment_id=experiment_id,
                             run_id=run_id,
                             operator_id=operator_id,
                             page=pagination_parameters.page,
                             page_size=pagination_parameters.page_size)
    return datasets
