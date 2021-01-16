# -*- coding: utf-8 -*-
"""Deployment Runs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers import DeploymentController, ProjectController
from projects.controllers.deployments.runs import RunController
from projects.database import session_scope

bp = Blueprint("deployment_runs", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_runs(session, project_id, deployment_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    runs = run_controller.list_runs(project_id=project_id,
                                    deployment_id=deployment_id)
    return jsonify(runs)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_runs(session, project_id, deployment_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run = run_controller.create_run(project_id=project_id,
                                    deployment_id=deployment_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["GET"])
@session_scope
def handle_get_run(session, project_id, deployment_id, run_id):
    """
    Handles GET requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run = run_controller.get_run(project_id=project_id,
                                 deployment_id=deployment_id,
                                 run_id=run_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["DELETE"])
@session_scope
def handle_delete_runs(session, project_id, deployment_id, run_id):
    """
    Handles DELETE requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run = run_controller.terminate_run(project_id=project_id,
                                       deployment_id=deployment_id,
                                       run_id=run_id)
    return jsonify(run)
