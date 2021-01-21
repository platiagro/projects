# -*- coding: utf-8 -*-
"""Deployments API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import projects.schemas.deployment
from projects.controllers import DeploymentController, OperatorController, \
    ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments",
)


@router.get("", response_model=projects.schemas.deployment.DeploymentList)
async def handle_list_deployments(project_id: str,
                                  session: Session = Depends(session_scope)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.deployment.DeploymentList
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployments = deployment_controller.list_deployments(project_id=project_id)
    return deployments


@router.post("", response_model=projects.schemas.deployment.Deployment)
async def handle_post_deployments(project_id: str,
                                  deployment: projects.schemas.deployment.DeploymentCreate,
                                  session: Session = Depends(session_scope)):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment = deployment_controller.create_deployment(project_id=project_id,
                                                         deployment=deployment)
    return deployment


@router.get("/{deployment_id}", response_model=projects.schemas.deployment.Deployment)
async def handle_get_deployment(project_id: str,
                                deployment_id: str,
                                session: Session = Depends(session_scope)):
    """
    Handles GET requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment = deployment_controller.get_deployment(deployment_id=deployment_id,
                                                      project_id=project_id)
    return deployment


@router.patch("/{deployment_id}", response_model=projects.schemas.deployment.Deployment)
async def handle_patch_deployment(project_id: str,
                                  deployment_id: str,
                                  deployment: projects.schemas.deployment.DeploymentUpdate,
                                  session: Session = Depends(session_scope)):
    """
    Handles PATCH requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment = deployment_controller.update_deployment(deployment_id=deployment_id,
                                                         project_id=project_id,
                                                         deployment=deployment)
    return deployment


@router.delete("/{deployment_id}")
async def handle_delete_deployment(project_id: str,
                                   deployment_id: str,
                                   session: Session = Depends(session_scope)):
    """
    Handles DELETE requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment = deployment_controller.delete_deployment(deployment_id=deployment_id,
                                                         project_id=project_id)
    return deployment


@router.patch("/{deployment_id}/operators/{operator_id}", response_model=projects.schemas.operator.Operator)
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
