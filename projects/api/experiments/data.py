# -*- coding: utf-8 -*-
"""Experiment Data API Router."""
import base64
import io
import zipfile
from typing import Optional

from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from projects.controllers import ExperimentController, ProjectController
from projects.database import session_scope
from projects.kfp.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.utils import get_volume_from_pod

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/data",
)

@router.get("")
async def handle_get_data(project_id: str,
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
    starlette.responses.StreamingResponse
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    file_as_b64 = get_volume_from_pod(volume_name=f"vol-tmp-data-{experiment_id}",
                                      namespace=KF_PIPELINES_NAMESPACE,
                                      experiment_id=experiment_id)

    # decoding as byte
    base64_bytes = file_as_b64.encode('ascii')
    file_as_bytes = base64.b64decode(base64_bytes)
    
    zip_file = io.BytesIO(file_as_bytes)

    response = StreamingResponse(zip_file, media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = "attachment; filename=results.zip"
    return response
    