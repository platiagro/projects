# -*- coding: utf-8 -*-
"""Tasks API Router."""
import base64
import os
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import projects.schemas.task
from projects.controllers import TaskController
from projects.database import session_scope
from projects.kubernetes.notebook import get_files_from_task
from projects.schemas.mailing import EmailSchema
from projects.utils import format_query_params

router = APIRouter(
    prefix="/tasks",
)


@router.get("", response_model=projects.schemas.task.TaskList)
async def handle_list_tasks(request: Request,
                            session: Session = Depends(session_scope)):
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
    task_controller = TaskController(session)
    filters = format_query_params(str(request.query_params))
    order_by = filters.pop("order", None)
    page = filters.pop("page", None)
    if page:
        page = int(page)
    page_size = filters.pop("page_size", None)
    if page_size:
        page_size = int(page_size)
    tasks = task_controller.list_tasks(page=page,
                                       page_size=page_size,
                                       order_by=order_by,
                                       **filters)
    return tasks


@router.post("", response_model=projects.schemas.task.Task)
async def handle_post_tasks(task: projects.schemas.task.TaskCreate,
                            background_tasks: BackgroundTasks,
                            session: Session = Depends(session_scope)):
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
async def handle_get_task(task_id: str,
                          session: Session = Depends(session_scope)):
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
async def handle_patch_task(task_id: str,
                            task: projects.schemas.task.TaskUpdate,
                            background_tasks: BackgroundTasks,
                            session: Session = Depends(session_scope)):
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
async def handle_delete_task(task_id: str,
                             background_tasks: BackgroundTasks,
                             session: Session = Depends(session_scope)):
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


@router.post("/{task_id}/email")
async def handle_task_email_sender(task_id: str,
                                   background_tasks: BackgroundTasks,
                                   email: EmailSchema,
                                   session: Session = Depends(session_scope)) -> JSONResponse:

    task_controller = TaskController(session)
    task = task_controller.get_task(task_id=task_id)
    



    template = f"""
            <html>
            <body>
            <p>  
            <br> Obrigado por usar a platiagro! Arquivos da tarefa '{task.name}' se encontram em anexo.
                 Esse email foi enviado automaticamente, por gentileza não responda.  
            </p>
    
            </body>
            </html>
         
            """
        
    # getting file contente as base64 string
    file_as_b64 = get_files_from_task(task.name)
    
    # decoding as byte
    base64_bytes = file_as_b64.encode('ascii')
    file_as_bytes = base64.b64decode(base64_bytes) 

    # using bytes to build the zipfile 
    with open('taskfiles.zip', 'wb') as f:
        f.write(file_as_bytes)
    f.close()
    
    message = MessageSchema(
        subject=f"Arquivos da tarefa '{task.name}'",
        recipients=["andreluizsplinter@gmail.com"],  # List of recipients, as many as you can pass 
        body=template,
        attachments=['taskfiles.zip'],
        subtype="html"
        )
    
    fm = FastMail(email.conf)
    background_tasks.add_task(fm.send_message,message)
    
    # removing file after send email
    os.remove('taskfiles.zip')
    
    return JSONResponse(status_code=200, content={"message": "email has been sent"})   
