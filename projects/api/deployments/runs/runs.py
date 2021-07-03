# -*- coding: utf-8 -*-
"""Runs API Router."""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session

from projects.controllers import DeploymentController, ProjectController
from projects.controllers.deployments.runs import RunController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/runs",
)


@router.get("")
async def handle_list_runs(project_id: str,
                           deployment_id: str,
                           session: Session = Depends(session_scope),
                           kubeflow_userid: Optional[str] = Header(None)):
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
    str
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    runs = run_controller.list_runs(project_id=project_id,
                                    deployment_id=deployment_id)
    return runs


@router.post("")
async def handle_post_runs(project_id: str,
                           deployment_id: str,
                           background_tasks: BackgroundTasks,
                           session: Session = Depends(session_scope),
                           kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    str
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session, background_tasks)
    run = run_controller.create_run(project_id=project_id,
                                    deployment_id=deployment_id)
    return run


@router.get("/{run_id}")
async def handle_get_run(project_id: str,
                         deployment_id: str,
                         run_id: str,
                         session: Session = Depends(session_scope),
                         kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles GET requests to /<run_id>.

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

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run = run_controller.get_run(project_id=project_id,
                                 deployment_id=deployment_id,
                                 run_id=run_id)
    return run


@router.delete("/{run_id}")
async def handle_delete_runs(project_id: str,
                             deployment_id: str,
                             run_id: str,
                             session: Session = Depends(session_scope),
                             kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles DELETE requests to /<run_id>.

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

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    run_controller = RunController(session)
    run = run_controller.terminate_run(project_id=project_id,
                                       deployment_id=deployment_id,
                                       run_id=run_id)
    return run
