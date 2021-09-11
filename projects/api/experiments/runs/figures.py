# -*- coding: utf-8 -*-
"""Figures API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects import database
from projects.controllers import (
    ExperimentController,
    FigureController,
    ProjectController,
)
from projects.controllers.experiments.runs import RunController

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/figures",
)


@router.get("")
async def handle_list_figures(
    project_id: str,
    experiment_id: str,
    run_id: str,
    operator_id: str,
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
    operator_id : str
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

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id, experiment_id)

    figure_controller = FigureController(session)
    figures = figure_controller.list_figures(
        project_id=project_id,
        experiment_id=experiment_id,
        run_id=run_id,
        operator_id=operator_id,
    )
    return figures
