# -*- coding: utf-8 -*-
"""Deployments Responses API Router."""
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from projects.controllers import DeploymentController, ProjectController, \
    ResponseController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/responses",
)


@router.post("")
async def handle_post_responses(project_id: str,
                                deployment_id: str,
                                body: dict = Body(...),
                                session: Session = Depends(session_scope)):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    body : fastapi.body
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    fastapi.responses.JSONResponse
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    response_controller = ResponseController(session)
    response_controller.create_response(project_id=project_id,
                                        deployment_id=deployment_id,
                                        body=body)

    return JSONResponse(
        status_code=200,
        content={"message": "OK"},
    )
