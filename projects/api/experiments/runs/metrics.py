# -*- coding: utf-8 -*-
"""Metrics API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from projects.controllers import ExperimentController, MetricController, \
    ProjectController
from projects.controllers.experiments.runs import RunController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/metrics",
)


@router.get("")
async def handle_list_metrics(project_id: str,
                              experiment_id: str,
                              run_id: str,
                              operator_id: str,
                              session: Session = Depends(session_scope),
                              kubeflow_userid: Optional[str] = Header("anonymous")):
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

    metric_controller = MetricController(session)
    metrics = metric_controller.list_metrics(project_id=project_id,
                                             experiment_id=experiment_id,
                                             operator_id=operator_id,
                                             run_id=run_id)
    return metrics
