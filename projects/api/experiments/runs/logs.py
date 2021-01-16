# -*- coding: utf-8 -*-
"""Experiment Logs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers import ExperimentController, ProjectController
from projects.controllers.experiments.runs.logs import LogController
from projects.database import session_scope

bp = Blueprint("experiment_logs", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_logs(session, project_id, experiment_id, run_id, operator_id):
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
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    log_controller = LogController(session)
    logs = log_controller.get_logs(project_id=project_id,
                                   experiment_id=experiment_id,
                                   run_id=run_id,
                                   operator_id=operator_id)
    return jsonify(logs)
