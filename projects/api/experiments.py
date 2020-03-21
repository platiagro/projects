# -*- coding: utf-8 -*-
"""Experiments blueprint."""

from flask import Blueprint, jsonify, request

from ..controllers.experiments import list_experiments, create_experiment, \
    get_experiment, update_experiment, delete_experiment
from ..utils import to_snake_case

bp = Blueprint("experiments", __name__)


@bp.route("", methods=["GET"])
def handle_list_experiments(project_id):
    """Handles GET requests to /."""
    return jsonify(list_experiments(project_id=project_id))


@bp.route("", methods=["POST"])
def handle_post_experiments(project_id):
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    experiment = create_experiment(project_id=project_id, **kwargs)
    return jsonify(experiment)


@bp.route("<experiment_id>", methods=["GET"])
def handle_get_experiment(project_id, experiment_id):
    """Handles GET requests to /<experiment_id>."""
    return jsonify(get_experiment(uuid=experiment_id,
                                  project_id=project_id))


@bp.route("<experiment_id>", methods=["PATCH"])
def handle_patch_experiment(project_id, experiment_id):
    """Handles PATCH requests to /<experiment_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    experiment = update_experiment(uuid=experiment_id,
                                   project_id=project_id,
                                   **kwargs)
    return jsonify(experiment)


@bp.route("<experiment_id>", methods=["DELETE"])
def handle_delete_experiment(project_id, experiment_id):
    """Handles DELETE requests to /<experiment_id>."""
    experiment = delete_experiment(uuid=experiment_id,
                                   project_id=project_id)
    return jsonify(experiment)
