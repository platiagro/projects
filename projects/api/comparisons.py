# -*- coding: utf-8 -*-
"""Comparison blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers.comparisons import list_comparisons, create_comparison, \
    update_comparison, delete_comparison
from projects.utils import to_snake_case

bp = Blueprint("comparisons", __name__)


@bp.route("", methods=["GET"])
def handle_list_comparisons(project_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    comparisons = list_comparisons(project_id=project_id)
    return jsonify(comparisons)


@bp.route("", methods=["POST"])
def handle_post_comparisons(project_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    comparison = create_comparison(project_id=project_id)
    return jsonify(comparison)


@bp.route("<comparison_id>", methods=["PATCH"])
def handle_patch_comparisons(project_id, comparison_id):
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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    comparison = update_comparison(comparison_id=comparison_id,
                                   project_id=project_id,
                                   **kwargs)
    return jsonify(comparison)


@bp.route("<comparison_id>", methods=["DELETE"])
def handle_delete_comparisons(project_id, comparison_id):
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
    comparison = delete_comparison(comparison_id=comparison_id,
                                   project_id=project_id)
    return jsonify(comparison)
