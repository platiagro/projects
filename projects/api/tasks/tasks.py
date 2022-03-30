# -*- coding: utf-8 -*-
"""Tasks API Router."""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

import projects.schemas.message
import projects.schemas.task
from projects import database
from projects.controllers import TaskController
from projects.schemas.mailing import EmailSchema

router = APIRouter(
    prefix="/tasks",
)

ATTACHMENT_FILE_NAME = "taskfiles.zip"


@router.post("/list_tasks", response_model=projects.schemas.task.TaskList)
async def handle_list_tasks(
    request_schema: projects.schemas.task.TaskListRequest,
    session: Session = Depends(database.session_scope),
):
    """
    Handles GET requests to /.
    Parameters
    ----------
    request : fastapi.Request
    session : sqlalchemy.orm.session.Session
    Returns
    -------
    projects.schemas.task.TaskList
    """
    request_as_dict = request_schema.dict()

    filters = request_as_dict.get("filters")
    order_by = request_as_dict.get("order")
    page = request_as_dict.get("page")
    page_size = request_as_dict.get("page_size")

    task_controller = TaskController(session)
    tasks = task_controller.list_tasks(
        page=page, page_size=page_size, order_by=order_by, **filters
    )
    return tasks


@router.post("", response_model=projects.schemas.task.Task)
async def handle_post_tasks(
    task: projects.schemas.task.TaskCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.session_scope),
):
    """
    Handles POST requests to /.

    Parameters
    ----------
    task : projects.schemas.task.TaskCreate
    background_tasks : fastapi.BackgroundTasks
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.task.Task
    """
    task_controller = TaskController(session, background_tasks)
    task = task_controller.create_task(task=task)
    return task


@router.get("/{task_id}", response_model=projects.schemas.task.Task)
async def handle_get_task(
    task_id: str, session: Session = Depends(database.session_scope)
):
    """
    Handles GET requests to /<task_id>.

    Parameters
    ----------
    task_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.task.Task
    """
    task_controller = TaskController(session)
    task = task_controller.get_task(task_id=task_id)
    return task


@router.patch("/{task_id}", response_model=projects.schemas.task.Task)
async def handle_patch_task(
    task_id: str,
    task: projects.schemas.task.TaskUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.session_scope),
):
    """
    Handles PATCH requests to /<task_id>.

    Parameters
    ----------
    task_id : str
    task : projects.schemas.task.TaskUpdate
    background_tasks : fastapi.BackgroundTasks
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.task.Task
    """
    task_controller = TaskController(session, background_tasks)
    task = task_controller.update_task(task_id=task_id, task=task)
    return task


@router.delete("/{task_id}")
async def handle_delete_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.session_scope),
):
    """
    Handles DELETE requests to /<task_id>.
    Parameters
    ----------
    task_id : str
    background_tasks : fastapi.BackgroundTasks
    session : sqlalchemy.orm.session.Session
    Returns
    -------
    projects.schemas.message.Message
    """
    task_controller = TaskController(session, background_tasks)
    result = task_controller.delete_task(task_id=task_id)
    return result


@router.post("/{task_id}/emails", status_code=200)
async def handle_task_email_sender(
    task_id: str,
    email_schema: EmailSchema,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.session_scope),
):
    """
    Handles request to /{task_id}/email

    Parameters
    ----------
    task_id : str
    background_tasks : fastapi.BackgroundTasks
    session : sqlalchemy.orm.session.Session
    email: projects.schema.mailing.EmailSchema

    Returns
    -------
    message: str

    """
    task_controller = TaskController(session, background_tasks)
    result = task_controller.send_emails(email_schema, task_id=task_id)

    return result
