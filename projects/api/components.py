# -*- coding: utf-8 -*-
"""Components blueprint."""

from flask import jsonify, request
from flask_smorest import Blueprint

from ..controllers.components import list_components, create_component, \
    get_component, update_component, delete_component, pagination_components
from ..utils import to_snake_case

bp = Blueprint("components", __name__)


@bp.route("", methods=["GET"])
def handle_list_components():
    """Handles GET requests to /."""
    return jsonify(list_components())


@bp.route("", methods=["POST"])
def handle_post_components():
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    component = create_component(**kwargs)
    return jsonify(component)


@bp.route("<component_id>", methods=["GET"])
def handle_get_component(component_id):
    """Handles GET requests to /<component_id>."""
    return jsonify(get_component(uuid=component_id))


@bp.route("<component_id>", methods=["PATCH"])
def handle_patch_component(component_id):
    """Handles PATCH requests to /<component_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    component = update_component(uuid=component_id, **kwargs)
    return jsonify(component)


@bp.route("<component_id>", methods=["DELETE"])
def handle_delete_component(component_id):
    """Handles DELETE requests to /<component_id>."""
    return jsonify(delete_component(uuid=component_id))

@bp.route("/", methods=["GET"])
@bp.paginate()
def handle_pagination(pagination_parameters):
    components = pagination_components(page=pagination_parameters.page, page_size=pagination_parameters.page_size)
    return jsonify(components)