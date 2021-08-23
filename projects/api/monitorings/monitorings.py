# -*- coding: utf-8 -*-
"""Monitorings API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.monitoring
from projects.controllers import DeploymentController, MonitoringController, \
    ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/monitorings",
)


@router.get("", response_model=projects.schemas.monitoring.MonitoringList)
async def handle_list_monitorings(project_id: str,
                                  deployment_id: str,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
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
async def handle_post_monitorings(project_id: str,
                                  deployment_id: str,
                                  monitoring: projects.schemas.monitoring.MonitoringCreate,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    monitoring : projects.schemas.monitoring.MonitoringCreate
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

    monitoring_controller = MonitoringController(session)
    monitoring = monitoring_controller.create_monitoring(deployment_id=deployment_id,
                                                         monitoring=monitoring)
    return monitoring


@router.delete("/{monitoring_id}")
async def handle_delete_monitorings(project_id: str,
                                    deployment_id: str,
                                    monitoring_id: str,
                                    session: Session = Depends(session_scope),
                                    kubeflow_userid: Optional[str] = Header("anonymous")):
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
