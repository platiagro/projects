# -*- coding: utf-8 -*-
"""Projects blueprint."""
from flask import jsonify, request
from flask_smorest import Blueprint

from projects.controllers.projects import create_project, get_project, \
    update_project, delete_project, list_projects, delete_multiple_projects
from projects.utils import to_snake_case

bp = Blueprint("projects", __name__)


@bp.route("", methods=["GET"])
@bp.paginate()
def handle_list_projects(pagination_parameters):
    """
    Handles GET requests to /.

    Parameters
    ----------
    pagination_parameters : flask_smorest.pagination.PaginationParameters

    Returns
    -------
    str
    """
    filters = request.args.copy()
    order_by = filters.pop("order", None)
    filters.pop("page", None)
    filters.pop("page_size", None)
    projects = list_projects(page=pagination_parameters.page,
                             page_size=pagination_parameters.page_size,
                             order_by=order_by,
                             **filters)
    return jsonify(projects)


@bp.route("", methods=["POST"])
def handle_post_projects():
    """
    Handles POST requests to /.

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = create_project(**kwargs)
    return jsonify(project)


@bp.route("<project_id>", methods=["GET"])
def handle_get_project(project_id):
    """
    Handles GET requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project = get_project(project_id=project_id)
    return jsonify(project)


@bp.route("<project_id>", methods=["PATCH"])
def handle_patch_project(project_id):
    """
    Handles PATCH requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = update_project(project_id=project_id, **kwargs)
    return jsonify(project)


@bp.route("<project_id>", methods=["DELETE"])
def handle_delete_project(project_id):
    """
    Handles DELETE requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    results = delete_project(project_id=project_id)
    return jsonify(results)


@bp.route("/deleteprojects", methods=["POST"])
def handle_post_deleteprojects():
    """
    Handles POST requests to /deleteprojects.

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    results = delete_multiple_projects(kwargs)
    return jsonify(results)
