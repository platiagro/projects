# -*- coding: utf-8 -*-
"""Operators blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import ExperimentController, \
    OperatorController, ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("operators", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_operators(session, project_id, experiment_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operators = operator_controller.list_operators(project_id=project_id,
                                                   experiment_id=experiment_id)
    return jsonify(operators)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_operator(session, project_id, experiment_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = operator_controller.create_operator(project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   **kwargs)
    return jsonify(operator)


@bp.route("<operator_id>", methods=["PATCH"])
@session_scope
def handle_patch_operator(session, project_id, experiment_id, operator_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    operator = operator_controller.update_operator(operator_id=operator_id,
                                                   project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   **kwargs)
    return jsonify(operator)


@bp.route("<operator_id>", methods=["DELETE"])
@session_scope
def handle_delete_operator(session, project_id, experiment_id, operator_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.delete_operator(operator_id=operator_id,
                                                   project_id=project_id,
                                                   experiment_id=experiment_id)
    return jsonify(operator)
