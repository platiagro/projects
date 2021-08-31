# -*- coding: utf-8 -*-
"""Logs API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects.controllers import DeploymentController, ProjectController
from projects.controllers.logs import LogController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/runs/{run_id}/logs",
)


@router.get("")
async def handle_list_logs(project_id: str,
                           deployment_id: str,
                           run_id: str,
                           session: Session = Depends(session_scope),
                           kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    str
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, kubeflow_userid=kubeflow_userid)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    log_controller = LogController(kubeflow_userid=kubeflow_userid)
    logs = log_controller.list_logs(project_id=project_id,
                                    deployment_id=deployment_id,
                                    run_id=run_id)
    return logs
