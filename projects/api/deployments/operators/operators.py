# -*- coding: utf-8 -*-
"""Deployments API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import projects.schemas.deployment
from projects.controllers import DeploymentController, OperatorController, \
    ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/operators",
)


@router.patch("/{operator_id}", response_model=projects.schemas.operator.Operator)
async def handle_patch_operator(project_id: str,
                                deployment_id: str,
                                operator_id: str,
                                operator: projects.schemas.operator.OperatorUpdate,
                                session: Session = Depends(session_scope)):
    """
    Handles PATCH requests to /<deployment_id>/operators/<operator_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    operator_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.operator.Operator
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    operator_controller = OperatorController(session)
    operator = operator_controller.update_operator(operator_id=operator_id,
                                                   project_id=project_id,
                                                   deployment_id=deployment_id,
                                                   operator=operator)
    return operator
