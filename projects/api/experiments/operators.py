# -*- coding: utf-8 -*-
"""Operators blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers.operators import list_operators, create_operator, \
    update_operator, delete_operator
from projects.utils import to_snake_case

bp = Blueprint("operators", __name__)


@bp.route("", methods=["GET"])
def handle_list_operators(project_id, experiment_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    str
    """
    return jsonify(list_operators(project_id=project_id,
                                  experiment_id=experiment_id))


@bp.route("", methods=["POST"])
def handle_post_operator(project_id, experiment_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = create_operator(project_id=project_id,
                               experiment_id=experiment_id,
                               **kwargs)
    return jsonify(operator)


@bp.route("<operator_id>", methods=["PATCH"])
def handle_patch_operator(project_id, experiment_id, operator_id):
    """
    Handles PATCH requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = update_operator(operator_id=operator_id,
                               project_id=project_id,
                               experiment_id=experiment_id,
                               **kwargs)
    return jsonify(operator)


@bp.route("<operator_id>", methods=["DELETE"])
def handle_delete_operator(project_id, experiment_id, operator_id):
    """
    Handles DELETE requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str

    Returns
    -------
    str
    """
    operator = delete_operator(operator_id=operator_id,
                               project_id=project_id,
                               experiment_id=experiment_id)
    return jsonify(operator)
