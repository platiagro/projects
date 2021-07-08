# -*- coding: utf-8 -*-
"""Runs API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.run
from projects.controllers import ExperimentController, ProjectController
from projects.controllers.experiments.runs import RunController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs",
)


@router.get("", response_model=projects.schemas.run.RunList)
async def handle_list_runs(project_id: str,
                           experiment_id: str,
                           session: Session = Depends(session_scope),
                           kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.run.RunList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    runs = run_controller.list_runs(project_id=project_id,
                                    experiment_id=experiment_id)
    return runs


@router.post("", response_model=projects.schemas.run.Run)
async def handle_post_run(project_id: str,
                          experiment_id: str,
                          session: Session = Depends(session_scope),
                          kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.run.Run
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.create_run(project_id=project_id,
                                    experiment_id=experiment_id)
    return run


@router.get("/{run_id}", response_model=projects.schemas.run.Run)
async def handle_get_run(project_id: str,
                         experiment_id: str,
                         run_id: str,
                         session: Session = Depends(session_scope),
                         kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.run.Run
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.get_run(project_id=project_id,
                                 experiment_id=experiment_id,
                                 run_id=run_id)
    return run


@router.delete("/{run_id}")
async def handle_delete_run(project_id: str,
                            experiment_id: str,
                            run_id: str,
                            session: Session = Depends(session_scope),
                            kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles DELETE requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.terminate_run(project_id=project_id,
                                       experiment_id=experiment_id,
                                       run_id=run_id)
    return run


@router.post("/{run_id}/retry")
async def handle_post_retry_run(project_id: str,
                                experiment_id: str,
                                run_id: str,
                                session: Session = Depends(session_scope),
                                kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /<run_id>/retry.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.retry_run(project_id=project_id,
                                   experiment_id=experiment_id,
                                   run_id=run_id)
    return run
