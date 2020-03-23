# -*- coding: utf-8 -*-
"""Parameters blueprint."""

from flask import Blueprint, jsonify

from ..controllers.parameters import list_parameters

bp = Blueprint("parameters", __name__)


@bp.route("", methods=["GET"])
def handle_list_parameters(component_id):
    """Handles GET requests to /."""
    return jsonify(list_parameters(component_id=component_id))
