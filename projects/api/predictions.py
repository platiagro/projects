# -*- coding: utf-8 -*-
"""Predictions blueprint."""

from flask import jsonify, request, Blueprint

from projects.controllers import DeploymentController, PredictionController, \
    ProjectController
from projects.database import session_scope

bp = Blueprint("predictions", __name__)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_prediction(session, project_id, deployment_id):
    """
    Handles POST request to /.

    Parameters
    -------
    project_id : str
    deployment_id : str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    deployment_controller = DeploymentController(session)
    deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

    prediction_controller = PredictionController(session)
    file = request.files.get("file")
    prediction = prediction_controller.create_prediction(project_id=project_id,
                                                         deployment_id=deployment_id,
                                                         file=file)
    return jsonify(prediction)
