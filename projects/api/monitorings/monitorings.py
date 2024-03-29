# -*- coding: utf-8 -*-
"""Monitorings API Router."""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.monitoring
from projects import database
from projects.controllers import (
    DeploymentController,
    MonitoringController,
    ProjectController,
)

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/monitorings",
)


@router.get("", response_model=projects.schemas.monitoring.MonitoringList)
async def handle_list_monitorings(
    project_id: str,
    deployment_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.monitoring.MonitoringList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    monitoring_controller = MonitoringController(session)
    monitorings = monitoring_controller.list_monitorings(deployment_id=deployment_id)
    return monitorings


@router.post("", response_model=projects.schemas.monitoring.Monitoring)
async def handle_post_monitorings(
    project_id: str,
    deployment_id: str,
    monitoring: projects.schemas.monitoring.MonitoringCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    monitoring : projects.schemas.monitoring.MonitoringCreate
    background_tasks : fastapi.BackgroundTasks
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.monitoring.Monitoring
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    monitoring_controller = MonitoringController(session, background_tasks)
    monitoring = monitoring_controller.create_monitoring(
        deployment_id=deployment_id, monitoring=monitoring
    )
    return monitoring


@router.delete("/{monitoring_id}")
async def handle_delete_monitorings(
    project_id: str,
    deployment_id: str,
    monitoring_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles DELETE requests to /<monitoring_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    monitoring_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    monitoring_controller = MonitoringController(session)
    response = monitoring_controller.delete_monitoring(uuid=monitoring_id)
    return response
