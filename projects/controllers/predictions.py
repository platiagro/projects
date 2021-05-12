# -*- coding: utf-8 -*-
"""Predictions controller."""
import json
from typing import Optional

import requests
from platiagro import load_dataset

from projects.controllers.utils import parse_dataframe_to_seldon_request, \
    parse_file_buffer_to_seldon_request
from projects.exceptions import BadRequest, InternalServerError
from projects.kubernetes.seldon import get_seldon_deployment_url


class PredictionController:
    def __init__(self, session):
        self.session = session

    def create_prediction(self, project_id: str, deployment_id: str, upload_file: Optional[bytes] = None, dataset: Optional[str] = None):
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
            request = parse_file_buffer_to_seldon_request(file=file._file)
        elif dataset is not None:
            try:
                dataset = load_dataset(dataset)
                request = parse_dataframe_to_seldon_request(dataframe=dataset)

            except AttributeError:
                request = parse_file_buffer_to_seldon_request(file=dataset)

            except FileNotFoundError:
                raise BadRequest("a valid dataset is required")

        else:
            raise BadRequest("either dataset name or file is required")

        url = get_seldon_deployment_url(deployment_id=deployment_id, external_url=False)
        response = requests.post(url, json=request)

        try:
            return json.loads(response._content)
        except json.decoder.JSONDecodeError:
            raise InternalServerError(response._content)
