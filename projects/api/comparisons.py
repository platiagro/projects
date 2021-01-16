# -*- coding: utf-8 -*-
"""Comparison blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import ComparisonController, ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("comparisons", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_comparisons(session, project_id):
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

    comparison_controller = ComparisonController(session)
    comparisons = comparison_controller.list_comparisons(project_id=project_id)
    return jsonify(comparisons)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_comparisons(session, project_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    with session_scope() as session:
        project_controller = ProjectController(session)
        project_controller.raise_if_project_does_not_exist(project_id)

        comparison_controller = ComparisonController(session)
        comparison = comparison_controller.create_comparison(project_id=project_id)
    return jsonify(comparison)


@bp.route("<comparison_id>", methods=["PATCH"])
@session_scope
def handle_patch_comparisons(session, project_id, comparison_id):
    """
    Handles PATCH requests to /<comparison_id>.

    Parameters
    ----------
    project_id : str
    comparison_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    comparison = comparison_controller.update_comparison(
        comparison_id=comparison_id,
        project_id=project_id,
        **kwargs,
    )
    return jsonify(comparison)


@bp.route("<comparison_id>", methods=["DELETE"])
@session_scope
def handle_delete_comparisons(session, project_id, comparison_id):
    """
    Handles DELETE requests to /<comparison_id>.

    Parameters
    ----------
    project_id : str
    comparison_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    comparison = comparison_controller.comparison_delete_comparison(
        comparison_id=comparison_id,
        project_id=project_id,
    )
    return jsonify(comparison)
