# -*- coding: utf-8 -*-
"""Predictions controller."""
import json

from typing import Optional

import requests
from platiagro import load_dataset

from projects.controllers.utils import (
    parse_dataframe_to_seldon_request,
    parse_file_buffer_to_seldon_request,
)
from projects import models
from projects.exceptions import BadRequest, InternalServerError
from projects.kubernetes.seldon import get_seldon_deployment_url


class PredictionController:
    def __init__(self, session, background_tasks=None):
        self.session = session
        self.background_tasks = background_tasks

    def create_prediction(
        self,
        deployment_id: str,
        prediction_id: str,
        upload_file: Optional[bytes] = None,
        dataset: Optional[str] = None,
    ):
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

        prediction_object = self.create_prediction_database_object(
            prediction_id=prediction_id,
            deployment_id=deployment_id,
            request_body={"foo": "bar"},
            response_body=None,
            status="started",
        )

        url = "http://10.50.11.49/seldon/anonymous/aedecb73-f4e6-4d70-b11a-0fdd50206935/api/v1.0/predictions"
        response = requests.post(url, json=request)

        try:
            response_content_json = json.loads(response._content)
        except json.decoder.JSONDecodeError:
            prediction_object.status = "failed"
            raise InternalServerError(response._content)

        prediction_object.status = "done"
        prediction_object.response_body = response_content_json
        return "No return implemented yet"

    def create_prediction_database_object(
        self,
        prediction_id: str,
        deployment_id: str,
        status: str,
        request_body: Optional[dict] = None,
        response_body: Optional[dict] = None,
    ):
        """
        Creates a prediction objec in database.

        Parameters
        ----------
        prediction_id : str
        deployment_id : str
        request_body: dict
        response_body: dict

        Returns
        -------
        <I have to figure out yet!>
        """
        prediction = models.Prediction(
            uuid=prediction_id,
            deployment_id=deployment_id,
            status=status,
            request_body=request_body,
            response_body=response_body,
        )

        self.session.add(prediction)
        self.session.commit()

        return prediction
