# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

from projects.controllers import MonitoringController, ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("monitorings", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_monitorings(session, project_id, deployment_id):
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

    controller = MonitoringController(session)
    monitorings = controller.list_monitorings(project_id=project_id,
                                              deployment_id=deployment_id)
    return jsonify(monitorings)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_monitorings(session, project_id, deployment_id):
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

    controller = MonitoringController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    monitoring = controller.create_monitoring(project_id=project_id,
                                              deployment_id=deployment_id,
                                              **kwargs)
    return jsonify(monitoring)


@bp.route("<monitoring_id>", methods=["DELETE"])
@session_scope
def handle_delete_monitorings(session, project_id, deployment_id, monitoring_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    controller = MonitoringController(session)
    response = controller.delete_monitoring(uuid=monitoring_id,
                                            project_id=project_id,
                                            deployment_id=deployment_id)
    return jsonify(response)
