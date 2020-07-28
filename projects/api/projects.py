# -*- coding: utf-8 -*-
"""Projects blueprint."""

from flask import jsonify, request
from flask_smorest import Blueprint
from ..controllers.projects import list_projects, create_project, \
    get_project, update_project, delete_project, pagination_projects, \
    total_rows_projects, delete_projects
from ..utils import to_snake_case

bp = Blueprint("projects", __name__)


@bp.route("", methods=["GET"])
@bp.paginate(page=0, page_size=0)
def handle_pagination_projects(pagination_parameters):
    name = request.args.get('name')
    total_rows = total_rows_projects(name=name)
    projects = pagination_projects(name=name,
                                   page=pagination_parameters.page,
                                   page_size=pagination_parameters.page_size)
    response = {
        'total': total_rows,
        'projects': projects
    }
    return jsonify(response)


@bp.route("", methods=["POST"])
def handle_post_projects():
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = create_project(**kwargs)
    return jsonify(project)


@bp.route("<project_id>", methods=["GET"])
def handle_get_project(project_id):
    """Handles GET requests to /<project_id>."""
    return jsonify(get_project(uuid=project_id))


@bp.route("<project_id>", methods=["PATCH"])
def handle_patch_project(project_id):
    """Handles PATCH requests to /<project_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = update_project(uuid=project_id, **kwargs)
    return jsonify(project)


@bp.route("<project_id>", methods=["DELETE"])
def handle_delete_project(project_id):
    """Handles DELETE requests to /<project_id>."""
    project = delete_project(uuid=project_id)
    return jsonify(project)


@bp.route("/deleteprojects", methods=["POST"])
def handle_delete_projects():
    kwargs = request.get_json(force=True)
    return jsonify(delete_projects(kwargs))
