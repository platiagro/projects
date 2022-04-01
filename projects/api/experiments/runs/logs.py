# -*- coding: utf-8 -*-
"""Logs API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects import database
from projects.controllers import ExperimentController, ProjectController
from projects.controllers.logs import LogController

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/logs",
)


@router.get("")
async def handle_list_logs(
    project_id: str,
    experiment_id: str,
    run_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    list
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    log_controller = LogController()
    logs = log_controller.list_logs(
        experiment_id=experiment_id, run_id=run_id
    )
    return logs
