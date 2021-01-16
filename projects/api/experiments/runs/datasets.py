# -*- coding: utf-8 -*-
"""Experiment Datasets blueprint."""
from flask import request, Blueprint

from projects.controllers import DatasetController, ExperimentController, \
    OperatorController, ProjectController
from projects.database import session_scope

bp = Blueprint("datasets", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_get_dataset(session, project_id, experiment_id, run_id, operator_id):
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
    List
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator_controller.raise_if_operator_does_not_exist(operator_id, experiment_id)

    dataset_controller = DatasetController(session)
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 10)
    application_type = request.headers.get("Accept", False)

    datasets = dataset_controller.get_dataset(project_id=project_id,
                                              experiment_id=experiment_id,
                                              run_id=run_id,
                                              operator_id=operator_id,
                                              page=int(page),
                                              page_size=int(page_size),
                                              application_csv=application_type)
    return datasets
