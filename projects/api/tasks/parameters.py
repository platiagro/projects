# -*- coding: utf-8 -*-
"""Parameters API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects.controllers import ParameterController, TaskController
from projects.database import session_scope

router = APIRouter(
    prefix="/tasks/{task_id}/parameters",
)


@router.get("")
async def handle_list_parameters(task_id: str,
                                 session: Session = Depends(session_scope),
                                 kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /.

    Parameters
    ----------
    task_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    dict
    """
    task_controller = TaskController(session)
    task_controller.raise_if_task_does_not_exist(task_id=task_id)

    parameter_controller = ParameterController(session)
    parameters = parameter_controller.list_parameters(task_id=task_id)
    return parameters
