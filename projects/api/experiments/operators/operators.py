# -*- coding: utf-8 -*-
"""Operators API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

import projects.schemas.operator
from projects import database
from projects.controllers import (
    ExperimentController,
    OperatorController,
    ProjectController,
)


router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/operators",
)


@router.get("", response_model=projects.schemas.operator.OperatorList)
async def handle_list_operators(
    project_id: str,
    experiment_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.operator.OperatorList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operators = operator_controller.list_operators(
        project_id=project_id, experiment_id=experiment_id
    )
    return operators


@router.post("", response_model=projects.schemas.operator.Operator)
async def handle_post_operator(
    project_id: str,
    experiment_id: str,
    operator: projects.schemas.operator.OperatorCreate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator : projects.schemas.operator.OperatorCreate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.operator.Operator
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.create_operator(
        project_id=project_id, experiment_id=experiment_id, operator=operator
    )
    return operator


@router.patch("/{operator_id}", response_model=projects.schemas.operator.Operator)
async def handle_patch_operator(
    project_id: str,
    experiment_id: str,
    operator_id: str,
    operator: projects.schemas.operator.OperatorUpdate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles PATCH requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    operator : projects.schemas.operator.OperatorUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.operator.Operator
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.update_operator(
        operator_id=operator_id,
        project_id=project_id,
        experiment_id=experiment_id,
        operator=operator,
    )
    return operator


@router.delete("/{operator_id}")
async def handle_delete_operator(
    project_id: str,
    experiment_id: str,
    operator_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles DELETE requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.delete_operator(
        operator_id=operator_id, project_id=project_id, experiment_id=experiment_id
    )
    return operator


@router.get("/eventsource")
async def handle_experiment_operator_stream(
    experiment_id: str, session: Session = Depends(database.session_scope)
):
    """
    Handle event source requests to /eventsource.

    Parameters
    ----------
    experiment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    EventSourceResponse
    """
    controller = OperatorController(session)
    stream = controller.watch_operator(experiment_id=experiment_id)

    return EventSourceResponse(stream)
