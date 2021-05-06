# -*- coding: utf-8 -*-
"""Predictions API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

from projects.controllers import DeploymentController, PredictionController, \
    ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/predictions",
)


@router.post("")
async def handle_post_prediction(project_id: str,
                                 deployment_id: str,
                                 request: Request,
                                 file: Optional[UploadFile] = File(None),
                                 session: Session = Depends(session_scope)):
    """
    Handles POST request to /.

    Parameters
    -------
    project_id : str
    deployment_id : str
    request : starlette.requests.Request
    file : starlette.datastructures.UploadFile
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    dict
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    # at this endpoint, we can accept both form-data and json as the request content-type
    kwargs = {}
    if file is not None:
        kwargs = {"upload_file": file}
    else:
        kwargs = await request.json()

    prediction_controller = PredictionController(session)
    return prediction_controller.create_prediction(project_id=project_id,
                                                   deployment_id=deployment_id,
                                                   **kwargs)
