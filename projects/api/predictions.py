# -*- coding: utf-8 -*-
"""Predictions blueprint."""

from flask import jsonify, request
from flask_smorest import Blueprint

from projects.controllers.predictions import list_predictions, create_prediction

bp = Blueprint("predictions", __name__)


@bp.route("", methods=["GET"])
def handle_get_predictions():
    """
    Handles GET requests to /.
    """
    predictions = list_predictions()
    return jsonify(predictions)


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
