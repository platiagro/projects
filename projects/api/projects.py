# -*- coding: utf-8 -*-
"""Projects blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("projects", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_projects(session):
    """
    Handles GET requests to /.

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    filters = request.args.copy()
    order_by = filters.pop("order", None)
    page = filters.pop("page", 1)
    page_size = filters.pop("page_size", 10)
    projects = project_controller.list_projects(page=int(page),
                                                page_size=int(page_size),
                                                order_by=order_by,
                                                **filters)
    return jsonify(projects)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_projects(session):
    """
    Handles POST requests to /.

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = project_controller.create_project(**kwargs)
    return jsonify(project)


@session_scope
@bp.route("<project_id>", methods=["GET"])
def handle_get_project(session, project_id):
    """
    Handles GET requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project = project_controller.get_project(project_id=project_id)
    return jsonify(project)


@session_scope
@bp.route("<project_id>", methods=["PATCH"])
def handle_patch_project(session, project_id):
    """
    Handles PATCH requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    project = project_controller.update_project(project_id=project_id, **kwargs)
    return jsonify(project)


@session_scope
@bp.route("<project_id>", methods=["DELETE"])
def handle_delete_project(session, project_id):
    """
    Handles DELETE requests to /<project_id>.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    results = project_controller.delete_project(project_id=project_id)
    return jsonify(results)


@session_scope
@bp.route("/deleteprojects", methods=["POST"])
def handle_post_deleteprojects(session):
    """
    Handles POST requests to /deleteprojects.

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    kwargs = request.get_json(force=True)
    results = project_controller.delete_multiple_projects(kwargs)
    return jsonify(results)
