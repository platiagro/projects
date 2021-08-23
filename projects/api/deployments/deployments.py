# -*- coding: utf-8 -*-
"""Deployments API Router."""
from typing import Optional
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, BackgroundTasks, Request, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.deployment
from projects.controllers import DeploymentController, ProjectController
from projects.database import session_scope
from projects.kubernetes.seldon import list_deployment_pods
from projects.kubernetes.utils import log_stream

router = APIRouter(
    prefix="/projects/{project_id}/deployments",
)


@router.get("", response_model=projects.schemas.deployment.DeploymentList)
async def handle_list_deployments(project_id: str,
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
    projects.schemas.deployment.DeploymentList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, kubeflow_userid=kubeflow_userid)
    deployments = deployment_controller.list_deployments(project_id=project_id)
    return deployments


@router.post("", response_model=projects.schemas.deployment.DeploymentList)
async def handle_post_deployments(project_id: str,
                                  deployment: projects.schemas.deployment.DeploymentCreate,
                                  background_tasks: BackgroundTasks,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, background_tasks, kubeflow_userid=kubeflow_userid)
    deployments = deployment_controller.create_deployment(project_id=project_id,
                                                          deployment=deployment)
    return deployments


@router.get("/{deployment_id}", response_model=projects.schemas.deployment.Deployment)
async def handle_get_deployment(project_id: str,
                                deployment_id: str,
                                session: Session = Depends(session_scope),
                                kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, kubeflow_userid=kubeflow_userid)
    deployment = deployment_controller.get_deployment(deployment_id=deployment_id)
    return deployment


@router.patch("/{deployment_id}", response_model=projects.schemas.deployment.Deployment)
async def handle_patch_deployment(project_id: str,
                                  deployment_id: str,
                                  deployment: projects.schemas.deployment.DeploymentUpdate,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles PATCH requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.deployment.Deployment
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, kubeflow_userid=kubeflow_userid)
    deployment = deployment_controller.update_deployment(deployment_id=deployment_id,
                                                         project_id=project_id,
                                                         deployment=deployment)
    return deployment


@router.delete("/{deployment_id}")
async def handle_delete_deployment(project_id: str,
                                   deployment_id: str,
                                   background_tasks: BackgroundTasks,
                                   session: Session = Depends(session_scope),
                                   kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles DELETE requests to /<deployment_id>.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session, background_tasks, kubeflow_userid=kubeflow_userid)
    deployment = deployment_controller.delete_deployment(deployment_id=deployment_id,
                                                         project_id=project_id)
    return deployment


@router.get("/{deployment_id}/logs/eventsource")
async def handle_log_deployment(deployment_id: str,
                                req: Request):
    """
    Handles log event source requests to /<deployment_id>/logs/eventsource.

    Parameters
    ----------
    deployment_id : str
    req : fastapi.Request

    Returns
    -------
    EventSourceResponse
    """
    pods = list_deployment_pods(deployment_id)
    if len(pods) == 1:
        pod = pods[0].metadata.name
        namespace = pods[0].metadata.namespace
        container = pods[0].spec.containers[0].name
        stream = log_stream(req, pod, namespace, container)
        return EventSourceResponse(stream)
    elif len(pods) == 0:
        return "unable to create log stream"
