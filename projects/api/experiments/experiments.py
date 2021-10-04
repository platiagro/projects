# -*- coding: utf-8 -*-
"""Experiments API Router."""

from typing import Optional
import asyncio

from fastapi import APIRouter, Depends, Header, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

import projects.schemas.experiment
from projects.controllers import ExperimentController, ProjectController, LogController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments",
)


@router.get("", response_model=projects.schemas.experiment.ExperimentList)
async def handle_list_experiments(project_id: str,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.experiment.ExperimentList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiments = experiment_controller.list_experiments(project_id=project_id)
    return experiments


@router.post("", response_model=projects.schemas.experiment.Experiment)
async def handle_post_experiments(project_id: str,
                                  experiment: projects.schemas.experiment.ExperimentCreate,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment : projects.schemas.experiment.ExperimentCreate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.experiment.Experiment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment = experiment_controller.create_experiment(project_id=project_id,
                                                         experiment=experiment)
    return experiment


@router.get("/{experiment_id}", response_model=projects.schemas.experiment.Experiment)
async def handle_get_experiment(project_id: str,
                                experiment_id: str,
                                session: Session = Depends(session_scope),
                                kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /<experiment_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.experiment.Experiment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment = experiment_controller.get_experiment(experiment_id=experiment_id,
                                                      project_id=project_id)
    return experiment


@router.patch("/{experiment_id}", response_model=projects.schemas.experiment.Experiment)
async def handle_patch_experiment(project_id: str,
                                  experiment_id: str,
                                  experiment: projects.schemas.experiment.ExperimentUpdate,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles PATCH requests to /<experiment_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    experiment : projects.schemas.experiment.ExperimentUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.experiment.Experiment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment = experiment_controller.update_experiment(experiment_id=experiment_id,
                                                         project_id=project_id,
                                                         experiment=experiment)
    return experiment


@router.delete("/{experiment_id}")
async def handle_delete_experiment(project_id: str,
                                   experiment_id: str,
                                   session: Session = Depends(session_scope),
                                   kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles DELETE requests to /<experiment_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment = experiment_controller.delete_experiment(experiment_id=experiment_id,
                                                         project_id=project_id)
    return experiment


@router.get("/{experiment_id}/logs/eventsource")
async def handle_log_deployment(req:Request, experiment_id: str):
    """
    Handles log event source requests to /<experiment_id>/logs/eventsource.

    Parameters
    ----------
    experiment_id : str
    Returns
    -------
    EventSourceResponse
    """

    controller = LogController()
    stream = controller.experiment_event_logs(experiment_id, req)
    return EventSourceResponse(stream)

