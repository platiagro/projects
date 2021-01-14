# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

from projects.controllers.monitorings import list_monitorings, \
    create_monitoring, delete_monitoring
from projects.utils import to_snake_case

bp = Blueprint("monitorings", __name__)


@bp.route("", methods=["GET"])
def handle_list_monitorings(project_id, deployment_id):
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
    return jsonify(list_monitorings(project_id=project_id, deployment_id=deployment_id))


@bp.route("", methods=["POST"])
def handle_post_monitorings(project_id, deployment_id):
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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    monitoring = create_monitoring(
        project_id=project_id,
        deployment_id=deployment_id,
        **kwargs)
    return jsonify(monitoring)


@bp.route("<monitoring_id>", methods=["DELETE"])
def handle_delete_monitorings(project_id, deployment_id, monitoring_id):
    """
    Handles DELETE requests to /<monitoring_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    monitoring_id : str

    Returns
    -------
    str
    """
    response = delete_monitoring(
        uuid=monitoring_id,
        project_id=project_id,
        deployment_id=deployment_id)
    return jsonify(response)
