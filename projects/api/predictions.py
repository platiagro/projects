# -*- coding: utf-8 -*-
"""Predictions API Router."""
from json.decoder import JSONDecodeError
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    Request,
    UploadFile,
    BackgroundTasks,
)
from sqlalchemy.orm import Session

from projects.controllers import (
    DeploymentController,
    PredictionController,
    ProjectController,
)
from projects.controllers.utils import uuid_alpha

from projects.exceptions import BadRequest
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/deployments/{deployment_id}/predictions",
)


@router.post("")
async def handle_post_prediction(
    project_id: str,
    deployment_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles POST request to /.

    Parameters
    -------
    project_id : str
    deployment_id : str
    request : starlette.requests.Request
    file : starlette.datastructures.UploadFile
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    dict
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    # at this endpoint, we can accept both form-data and json as the request content-type
    kwargs = {}
    if file is not None:
        kwargs = {"upload_file": file}
    else:
        try:
            kwargs = await request.json()
        except JSONDecodeError:
            raise BadRequest("either form-data or json is required")

    prediction_promise_uuid = str(uuid_alpha())

    prediction_controller = PredictionController(session, background_tasks)
    prediction_controller.create_prediction(
        deployment_id=deployment_id, prediction_id=prediction_promise_uuid, **kwargs
    )

    return {"prediction_id": prediction_promise_uuid}
