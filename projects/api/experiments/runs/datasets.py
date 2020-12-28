# -*- coding: utf-8 -*-
"""Experiment Datasets blueprint."""
from flask import request, Blueprint

from projects.controllers.experiments.runs.datasets import get_dataset

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
def handle_get_dataset(project_id, experiment_id, run_id, operator_id):
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
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 10)
    application_type = request.headers.get("Accept", False)

    datasets = get_dataset(project_id=project_id,
                           experiment_id=experiment_id,
                           run_id=run_id,
                           operator_id=operator_id,
                           page=int(page),
                           page_size=int(page_size),
                           application_csv=application_type)

    return datasets
