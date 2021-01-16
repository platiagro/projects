# -*- coding: utf-8 -*-
"""Deployments blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import DeploymentController, OperatorController, \
    ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("deployments", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_deployments(session, project_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployments = deployment_controller.list_deployments(project_id=project_id)
    return jsonify(deployments)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_deployments(session, project_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    deployment = deployment_controller.create_deployment(project_id=project_id, **kwargs)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["GET"])
@session_scope
def handle_get_deployment(session, project_id, deployment_id):
    """
    Handles GET requests to /<deployment_id>.

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
    deployment = deployment_controller.get_deployment(deployment_id=deployment_id,
                                                      project_id=project_id)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["PATCH"])
@session_scope
def handle_patch_deployment(session, project_id, deployment_id):
    """
    Handles PATCH requests to /<deployment_id>.

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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    deployment = deployment_controller.update_deployment(deployment_id=deployment_id,
                                                         project_id=project_id,
                                                         **kwargs)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["DELETE"])
@session_scope
def handle_delete_deployment(session, project_id, deployment_id):
    """
    Handles DELETE requests to /<deployment_id>.

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
    deployment = deployment_controller.delete_deployment(deployment_id=deployment_id,
                                                         project_id=project_id)
    return jsonify(deployment)


@bp.route("<deployment_id>/operators/<operator_id>", methods=["PATCH"])
@session_scope
def handle_patch_operator(session, project_id, deployment_id, operator_id):
    """
    Handles PATCH requests to /<deployment_id>/operators/<operator_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    operator_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = OperatorController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = deployment_controller.update_operator(operator_id=operator_id,
                                                     project_id=project_id,
                                                     deployment_id=deployment_id,
                                                     **kwargs)
    return operator
