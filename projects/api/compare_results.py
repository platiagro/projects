# -*- coding: utf-8 -*-
"""Compare results blueprint."""

from flask import Blueprint, jsonify, request

from ..controllers.compare_results import list_compare_results, create_compare_result, \
    update_compare_result, delete_compare_result
from ..utils import to_snake_case

bp = Blueprint("compare_results", __name__)


@bp.route("", methods=["GET"])
def handle_list_experiments(project_id):
    """Handles GET requests to /."""
    return jsonify(list_compare_results(project_id=project_id))


@bp.route("", methods=["POST"])
def handle_post_experiments(project_id):
    """Handles POST requests to /."""
    compare_result = create_compare_result(project_id=project_id)
    return jsonify(compare_result)


@bp.route("<compare_result_id>", methods=["PATCH"])
def handle_patch_experiment(project_id, compare_result_id):
    """Handles PATCH requests to /<compare_result_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    experiment = update_compare_result(uuid=compare_result_id, project_id=project_id, **kwargs)
    return jsonify(experiment)


@bp.route("<compare_result_id>", methods=["DELETE"])
def handle_delete_experiment(project_id, compare_result_id):
    """Handles DELETE requests to /<compare_result_id>."""
    experiment = delete_compare_result(uuid=compare_result_id, project_id=project_id)
    return jsonify(experiment)
