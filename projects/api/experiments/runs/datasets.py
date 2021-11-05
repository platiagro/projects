# -*- coding: utf-8 -*-
"""Datasets API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects import database
from projects.controllers import (
    DatasetController,
    ExperimentController,
    OperatorController,
    ProjectController,
)
from projects.controllers.experiments.runs import RunController

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets",
)


@router.get("")
async def handle_get_dataset(
    project_id: str,
    experiment_id: str,
    run_id: str,
    operator_id: str,
    page: Optional[int] = 1,
    page_size: Optional[int] = 10,
    accept: Optional[str] = Header(None),
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
    List
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator_controller.raise_if_operator_does_not_exist(operator_id)

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id, experiment_id)

    dataset_controller = DatasetController(session)
    datasets = dataset_controller.get_dataset(
        project_id=project_id,
        experiment_id=experiment_id,
        run_id=run_id,
        operator_id=operator_id,
        page=page,
        page_size=page_size,
        accept=accept,
    )
    return datasets
