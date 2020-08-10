# -*- coding: utf-8 -*-
"""Tasks blueprint."""

from flask import jsonify, request
from flask_smorest import Blueprint

from ..controllers.tasks import create_task, get_task, update_task, \
     delete_task, pagination_tasks, total_rows_tasks
from ..utils import to_snake_case

bp = Blueprint("tasks", __name__)


@bp.route("", methods=["GET"])
@bp.paginate(page=0)
def handle_list_tasks(pagination_parameters):
    name = request.args.get('name')
    total_rows = total_rows_tasks(name=name)
    tasks = pagination_tasks(name=name,
                                       page=pagination_parameters.page,
                                       page_size=pagination_parameters.page_size)
    response = {
        'total': total_rows,
        'tasks': tasks
    }
    return jsonify(response)


@bp.route("", methods=["POST"])
def handle_post_tasks():
    """Handles POST requests to /."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = create_task(**kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["GET"])
def handle_get_task(task_id):
    """Handles GET requests to /<task_id>."""
    return jsonify(get_task(uuid=task_id))


@bp.route("<task_id>", methods=["PATCH"])
def handle_patch_task(task_id):
    """Handles PATCH requests to /<task_id>."""
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    task = update_task(uuid=task_id, **kwargs)
    return jsonify(task)


@bp.route("<task_id>", methods=["DELETE"])
def handle_delete_task(task_id):
    """Handles DELETE requests to /<task_id>."""
    return jsonify(delete_task(uuid=task_id))
