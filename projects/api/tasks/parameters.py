# -*- coding: utf-8 -*-
"""Parameters blueprint."""

from flask import Blueprint, jsonify

from projects.controllers.tasks.parameters import list_parameters

bp = Blueprint("parameters", __name__)


@bp.route("", methods=["GET"])
def handle_list_parameters(task_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    parameters = list_parameters(task_id=task_id)
    return jsonify(parameters)
