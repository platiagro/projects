# -*- coding: utf-8 -*-
"""Predictions controller."""
import json

import requests
from platiagro import load_dataset

from projects.controllers.utils import parse_dataframe_to_seldon_request, \
    parse_file_buffer_to_seldon_request
from projects.exceptions import BadRequest, InternalServerError
from projects.kubernetes.seldon import get_seldon_deployment_url


class PredictionController:
    def __init__(self, session):
        self.session = session

    def create_prediction(self, project_id: str, deployment_id: str, upload_file: bytes = None, dataset: str = None):
        """
        POST a prediction file to seldon deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        upload_file : starlette.datastructures.UploadFile
            File buffer.
        dataset : str
            Dataset name.

        Returns
        -------
        dict
        """
        if upload_file is not None:
            file = upload_file.file
            request = parse_file_buffer_to_seldon_request(file=file)
        elif dataset is not None:
            try:
                dataframe = load_dataset(dataset)
            except FileNotFoundError:
                raise BadRequest("a valid dataset is required")
            request = parse_dataframe_to_seldon_request(dataframe=dataframe)
        else:
            raise BadRequest("either dataset name or file is required")

        url = get_seldon_deployment_url(deployment_id=deployment_id, external_url=False)
        response = requests.post(url, json=request)

        try:
            return json.loads(response._content)
        except json.decoder.JSONDecodeError:
            raise InternalServerError(response._content)
