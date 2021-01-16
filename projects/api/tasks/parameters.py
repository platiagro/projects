# -*- coding: utf-8 -*-
"""Parameters blueprint."""

from flask import Blueprint, jsonify

from projects.controllers import ParameterController
from projects.database import session_scope

bp = Blueprint("parameters", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_parameters(session, task_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    parameter_controller = ParameterController(session)
    parameters = parameter_controller.list_parameters(task_id=task_id)
    return jsonify(parameters)
