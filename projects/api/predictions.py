# -*- coding: utf-8 -*-
"""Predictions blueprint."""

from flask import jsonify, request, Blueprint

from projects.controllers.predictions import create_prediction

bp = Blueprint("predictions", __name__)


@bp.route("", methods=["POST"])
def handle_post_prediction(project_id, deployment_id):
    """
    Handles POST request to /.

    Parameters
    -------
    project_id : str
    deployment_id : str
    """
    file = request.files.get("file")
    prediction = create_prediction(project_id, deployment_id, file)
    return jsonify(prediction)
