# -*- coding: utf-8 -*-
"""Deployments blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers.deployments import create_deployment, \
    delete_deployment, get_deployment, list_deployments, update_deployment
from projects.controllers.operators import update_operator
from projects.utils import to_snake_case

bp = Blueprint("deployments", __name__)


@bp.route("", methods=["GET"])
def handle_list_deployments(project_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    deployments = list_deployments(project_id=project_id)
    return jsonify(deployments)


@bp.route("", methods=["POST"])
def handle_post_deployments(project_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    deployment = create_deployment(project_id=project_id, **kwargs)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["GET"])
def handle_get_deployment(project_id, deployment_id):
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
    deployment = get_deployment(deployment_id=deployment_id,
                                project_id=project_id)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["PATCH"])
def handle_patch_deployment(project_id, deployment_id):
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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    deployment = update_deployment(deployment_id=deployment_id,
                                   project_id=project_id,
                                   **kwargs)
    return jsonify(deployment)


@bp.route("<deployment_id>", methods=["DELETE"])
def handle_delete_deployment(project_id, deployment_id):
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
    deployment = delete_deployment(deployment_id=deployment_id,
                                   project_id=project_id)
    return jsonify(deployment)


@bp.route("<deployment_id>/operators/<operator_id>", methods=["PATCH"])
def handle_patch_operator(project_id, deployment_id, operator_id):
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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = update_operator(operator_id=operator_id,
                               project_id=project_id,
                               deployment_id=deployment_id,
                               **kwargs)
    return jsonify(operator)
