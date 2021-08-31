# -*- coding: utf-8 -*-
"""Monitorings API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects.controllers import DeploymentController, MonitoringController, \
    MonitoringFigureController, ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}/figures",
)


@router.get("")
async def handle_list_figures_monitorings(project_id: str,
                                          deployment_id: str,
                                          monitoring_id: str,
                                          session: Session = Depends(session_scope),
                                          kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    monitoring_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    list
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, kubeflow_userid=kubeflow_userid)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    monitoring_controller = MonitoringController(session, kubeflow_userid=kubeflow_userid)
    monitoring_controller.raise_if_monitoring_does_not_exist(monitoring_id)

    monitoring_figure_controller = MonitoringFigureController(session)
    figures_monitoring = monitoring_figure_controller.list_figures(project_id=project_id,
                                                                   deployment_id=deployment_id,
                                                                   monitoring_id=monitoring_id)
    return figures_monitoring
