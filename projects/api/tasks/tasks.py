# -*- coding: utf-8 -*-
"""Tasks blueprint."""
from flask import jsonify, request
from flask_smorest import Blueprint

from projects.controllers.tasks import create_task, delete_task, get_task, \
    list_tasks, update_task
from projects.utils import to_snake_case

bp = Blueprint("tasks", __name__)


@bp.route("", methods=["GET"])
@bp.paginate()
def handle_list_tasks(pagination_parameters):
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
    tasks = list_tasks(page=pagination_parameters.page,
                       page_size=pagination_parameters.page_size,
                       order_by=order_by,
                       **filters)
    return jsonify(tasks)


@bp.route("", methods=["POST"])
def handle_post_tasks():
    """
    Handles POST requests to /.

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = create_task(**kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["GET"])
def handle_get_task(task_id):
    """
    Handles GET requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    task = get_task(task_id=task_id)
    return jsonify(task)


@bp.route("<task_id>", methods=["PATCH"])
def handle_patch_task(task_id):
    """
    Handles PATCH requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = update_task(task_id=task_id, **kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["DELETE"])
def handle_delete_task(task_id):
    """
    Handles DELETE requests to /<task_id>.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    str
    """
    result = delete_task(task_id=task_id)
    return jsonify(result)
