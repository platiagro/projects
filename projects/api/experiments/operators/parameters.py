# -*- coding: utf-8 -*-
"""Operators blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers.operators.parameters import update_parameter
from projects.utils import to_snake_case

bp = Blueprint("operator_parameters", __name__)


@bp.route("<name>", methods=["PATCH"])
def handle_patch_parameter(project_id, experiment_id, operator_id, name):
    """
    Handles PATCH requests to /<name>.

    Parameters
    ----------
    name : str
        Parameter name.
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    parameter = update_parameter(
        project_id=project_id,
        experiment_id=experiment_id,
        operator_id=operator_id,
        name=name,
        **kwargs
    )
    return jsonify(parameter)
