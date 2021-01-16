# -*- coding: utf-8 -*-
"""Tasks blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import TaskController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("tasks", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_tasks(session):
    """
    Handles GET requests to /.

    Returns
    -------
    str
    """
    task_controller = TaskController(session)
    filters = request.args.copy()
    order_by = filters.pop("order", None)
    page = filters.pop("page", None)
    page_size = filters.pop("page_size", None)
    tasks = task_controller.list_tasks(page=page,
                                       page_size=page_size,
                                       order_by=order_by,
                                       **filters)
    return jsonify(tasks)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_tasks(session):
    """
    Handles POST requests to /.

    Returns
    -------
    str
    """
    task_controller = TaskController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = task_controller.create_task(**kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["GET"])
@session_scope
def handle_get_task(session, task_id):
    """
    Handles GET requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    task_controller = TaskController(session)
    task = task_controller.get_task(task_id=task_id)
    return jsonify(task)


@bp.route("<task_id>", methods=["PATCH"])
@session_scope
def handle_patch_task(session, task_id):
    """
    Handles PATCH requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    task_controller = TaskController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = task_controller.update_task(task_id=task_id, **kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["DELETE"])
@session_scope
def handle_delete_task(session, task_id):
    """
    Handles DELETE requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    task_controller = TaskController(session)
    result = task_controller.delete_task(task_id=task_id)
    return jsonify(result)
