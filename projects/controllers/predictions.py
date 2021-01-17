# -*- coding: utf-8 -*-
"""Predictions controller."""
import json

import requests
from projects.exceptions import InternalServerError

from projects.controllers.utils import parse_file_buffer_to_seldon_request
from projects.kubernetes.seldon import get_seldon_deployment_url


class PredictionController:
    def __init__(self, session):
        self.session = session

    def create_prediction(self, project_id: str, deployment_id: str, file: bytes = None):
        """
        POST a prediction file to seldon deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        file : bytes
            File buffer.

        Returns
        -------
        dict
        """
        url = get_seldon_deployment_url(deployment_id)
        request = parse_file_buffer_to_seldon_request(file)
        response = requests.post(url, json=request)

        try:
            return json.loads(response._content)
        except json.decoder.JSONDecodeError:
            raise InternalServerError(response._content)
