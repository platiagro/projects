# -*- coding: utf-8 -*-
"""Deployment Logs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers import DeploymentController, ProjectController
from projects.controllers.deployments.runs.logs import LogController
from projects.database import session_scope

bp = Blueprint("deployment_logs", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_logs(session, project_id, deployment_id, run_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    log_controller = LogController(session)
    logs = log_controller.list_logs(project_id=project_id,
                                    deployment_id=deployment_id,
                                    run_id=run_id)
    return jsonify(logs)
