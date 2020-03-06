# -*- coding: utf-8 -*-
"""Experiments components blueprint."""

from flask import Blueprint, jsonify, request

from ..controllers.experiments_components import list_components, \
    create_component, delete_component
from ..utils import to_snake_case

bp = Blueprint("experiments_components", __name__)


@bp.route("", methods=["GET"])
def handle_list_components(project_id, experiment_id):
    """Handles GET requests to /."""
    return jsonify(list_components(project_id=project_id,
                                   experiment_id=experiment_id))


@bp.route("", methods=["POST"])
def handle_post_components(project_id, experiment_id):
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    component = create_component(project_id=project_id,
                                 experiment_id=experiment_id,
                                 **kwargs)
    return jsonify(component)


@bp.route("<experiment_component_id>", methods=["DELETE"])
def handle_delete_component(project_id, experiment_id, experiment_component_id):
    """Handles PATCH requests to /<experiment_component_id>."""
    component = delete_component(uuid=experiment_component_id)
    return jsonify(component)