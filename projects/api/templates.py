# -*- coding: utf-8 -*-
"""Templates blueprint."""

from flask import Blueprint, jsonify, request

from ..controllers.templates import list_templates, create_template, \
    get_template, update_template, delete_template
from ..utils import to_snake_case

bp = Blueprint("templates", __name__)


@bp.route("", methods=["GET"])
def handle_list_templates():
    """Handles GET requests to /."""
    return jsonify(list_templates())


@bp.route("", methods=["POST"])
def handle_post_templates():
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    template = create_template(**kwargs)
    return jsonify(template)


@bp.route("<template_id>", methods=["GET"])
def handle_get_template(template_id):
    """Handles GET requests to /<template_id>."""
    return jsonify(get_template(uuid=template_id))


@bp.route("<template_id>", methods=["PATCH"])
def handle_patch_template(template_id):
    """Handles PATCH requests to /<template_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    template = update_template(uuid=template_id, **kwargs)
    return jsonify(template)


@bp.route("<template_id>", methods=["DELETE"])
def handle_delete_template(template_id):
    """Handles DELETE requests to /<template_id>."""
    template = delete_template(uuid=template_id)
    return jsonify(template)
