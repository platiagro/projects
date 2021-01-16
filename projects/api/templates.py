# -*- coding: utf-8 -*-
"""Templates blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import TemplateController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("templates", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_templates(session):
    """
    Handles GET requests to /.
    """
    template_controller = TemplateController(session)
    templates = template_controller.list_templates()
    return jsonify(templates)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_templates(session):
    """
    Handles POST requests to /.
    """
    template_controller = TemplateController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    template = template_controller.create_template(**kwargs)
    return jsonify(template)


@bp.route("<template_id>", methods=["GET"])
@session_scope
def handle_get_template(session, template_id):
    """
    Handles GET requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    """
    template_controller = TemplateController(session)
    template = template_controller.get_template(template_id=template_id)
    return jsonify(template)


@bp.route("<template_id>", methods=["PATCH"])
@session_scope
def handle_patch_template(session, template_id):
    """
    Handles PATCH requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    """
    template_controller = TemplateController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    template = template_controller.update_template(template_id=template_id, **kwargs)
    return jsonify(template)


@bp.route("<template_id>", methods=["DELETE"])
@session_scope
def handle_delete_template(session, template_id):
    """
    Handles DELETE requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    """
    template_controller = TemplateController(session)
    template = template_controller.delete_template(template_id=template_id)
    return jsonify(template)
