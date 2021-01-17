# -*- coding: utf-8 -*-
"""Logs API Router."""
from fastapi import APIRouter, Depends

from projects.controllers import DeploymentController, ProjectController
from projects.controllers.deployments.runs import RunController
from projects.controllers.deployments.runs.logs import LogController
from projects.database import Session, session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/logs",
)


@router.get("")
async def handle_list_logs(project_id: str,
                           deployment_id: str,
                           run_id: str,
                           session: Session = Depends(session_scope)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id)

    log_controller = LogController(session)
    logs = log_controller.list_logs(project_id=project_id,
                                    deployment_id=deployment_id,
                                    run_id=run_id)
    return logs
