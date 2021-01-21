# -*- coding: utf-8 -*-
"""Logs API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from projects.controllers import ExperimentController, ProjectController
from projects.controllers.experiments.runs.logs import LogController
from projects.controllers.experiments.runs import RunController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/logs",
)


@router.get("")
async def handle_list_logs(project_id: str,
                           experiment_id: str,
                           run_id: str,
                           operator_id: str,
                           session: Session = Depends(session_scope)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    operator_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    list
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id, experiment_id)

    log_controller = LogController(session)
    logs = log_controller.get_logs(project_id=project_id,
                                   experiment_id=experiment_id,
                                   run_id=run_id,
                                   operator_id=operator_id)
    return logs
