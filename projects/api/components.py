# -*- coding: utf-8 -*-
"""Components blueprint."""

from flask import jsonify, request
from flask_smorest import Blueprint

from ..controllers.components import create_component, get_component, update_component, \
     delete_component, pagination_components, total_rows_components
from ..utils import to_snake_case

bp = Blueprint("components", __name__)


@bp.route("", methods=["GET"])
@bp.paginate(page=0)
def handle_list_components(pagination_parameters):
    name = request.args.get('name')
    order = request.args.get('order')
    total_rows = total_rows_components(name=name)
    components = pagination_components(name=name,
                                       page=pagination_parameters.page,
                                       page_size=pagination_parameters.page_size, order=order)
    response = {
        'total': total_rows,
        'components': components
    }
    return jsonify(response)


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
