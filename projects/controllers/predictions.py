# -*- coding: utf-8 -*-
"""Predictions controller."""
import json

import requests
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, InternalServerError

from projects.controllers.deployments import DeploymentController
from projects.controllers.projects import ProjectController
from projects.controllers.utils import parse_file_buffer_to_seldon_request
from projects.kubernetes.seldon import get_seldon_deployment_url


class PredictionController:
    def __init__(self, session):
        self.session = session
        self.project_controller = ProjectController(session)
        self.deployment_controller = DeploymentController(session)

    def create_prediction(self, project_id=None, deployment_id=None, file=None):
        """
        POST a prediction file to seldon deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        file : dict
            CSV file bufffer.

        Returns
        -------
        dict

        Raises
        ------
        BadRequest
            When `file` is missing.

        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        if not isinstance(file, FileStorage):
            raise BadRequest("file is required.")

        url = get_seldon_deployment_url(deployment_id)
        request = parse_file_buffer_to_seldon_request(file)
        response = requests.post(url, json=request)

        try:
            return json.loads(response._content)
        except json.decoder.JSONDecodeError:
            raise InternalServerError(response._content)
