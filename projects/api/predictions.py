# -*- coding: utf-8 -*-
"""Predictions API Router."""
from fastapi import APIRouter, Depends, File, UploadFile
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
                                 file: UploadFile = File(...),
                                 session: Session = Depends(session_scope)):
    """
    Handles POST request to /.

    Parameters
    -------
    project_id : str
    deployment_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    dict
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    prediction_controller = PredictionController(session)
    prediction = prediction_controller.create_prediction(project_id=project_id,
                                                         deployment_id=deployment_id,
                                                         file=file)
    return prediction
