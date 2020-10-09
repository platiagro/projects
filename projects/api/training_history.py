# -*- coding: utf-8 -*-
"""Training history blueprint."""

from flask import Blueprint, jsonify, request

from ..controllers.training_history import list_training_history, create_training_history, \
    delete_training_history
from ..utils import to_snake_case

bp = Blueprint("training_history", __name__)


@bp.route("", methods=["GET"])
def handle_list_training_history(project_id, experiment_id):
    """Handles GET requests to /."""
    return jsonify(list_training_history(project_id=project_id, experiment_id=experiment_id))


@bp.route("", methods=["POST"])
def handle_post_training_history(project_id, experiment_id):
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    response = create_training_history(project_id=project_id,
                                       experiment_id=experiment_id,
                                       **kwargs)
    return jsonify(response)


@bp.route("<training_history_id>", methods=["DELETE"])
def handle_delete_training_history(project_id, experiment_id, training_history_id):
    """Handles DELETE requests to /<training_history_id>."""
    response = delete_training_history(uuid=training_history_id,
                                       project_id=project_id,
                                       experiment_id=experiment_id)
    return jsonify(response)
