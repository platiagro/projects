# -*- coding: utf-8 -*-
"""Operators API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import projects.schemas.operator
from projects.controllers import ExperimentController, OperatorController, \
    ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/operators",
)


@router.get("", response_model=projects.schemas.operator.OperatorList)
async def handle_list_operators(project_id: str,
                                experiment_id: str,
                                session: Session = Depends(session_scope)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.operator.OperatorList
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operators = operator_controller.list_operators(project_id=project_id,
                                                   experiment_id=experiment_id)
    return operators


@router.post("", response_model=projects.schemas.operator.Operator)
async def handle_post_operator(project_id: str,
                               experiment_id: str,
                               operator: projects.schemas.operator.OperatorCreate,
                               session: Session = Depends(session_scope)):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator : projects.schemas.operator.OperatorCreate
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.operator.Operator
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.create_operator(project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   operator=operator)
    return operator


@router.patch("/{operator_id}", response_model=projects.schemas.operator.Operator)
async def handle_patch_operator(project_id: str,
                                experiment_id: str,
                                operator_id: str,
                                operator: projects.schemas.operator.OperatorUpdate,
                                session: Session = Depends(session_scope)):
    """
    Handles PATCH requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    operator : projects.schemas.operator.OperatorUpdate
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.operator.Operator
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.update_operator(operator_id=operator_id,
                                                   project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   operator=operator)
    return operator


@router.delete("/{operator_id}")
async def handle_delete_operator(project_id: str,
                                 experiment_id: str, operator_id: str,
                                 session: Session = Depends(session_scope)):
    """
    Handles DELETE requests to /<operator_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.delete_operator(operator_id=operator_id,
                                                   project_id=project_id,
                                                   experiment_id=experiment_id)
    return operator
