# -*- coding: utf-8 -*-
"""Predictions controller."""
import json
import asyncio

from requests.api import request
from projects.models import deployment, response
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

import time


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

        url = get_seldon_deployment_url(deployment_id=deployment_id, external_url=False)
        response = requests.post(url, json=request)

        try:
            response_content_json = json.loads(response._content)
        except json.decoder.JSONDecodeError:
            self.create_prediction_database_object(
                prediction_id,
                deployment_id,
                failed=True
            )
            raise InternalServerError(response._content)

        self.create_prediction_database_object(
            prediction_id,
            deployment_id,
            request,
            response_content_json,
        )
        return "No return implemented yet"

    def create_prediction_database_object(
        self, prediction_id, deployment_id, request_body, response_body, **kwargs
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
        if kwargs.get("failed") == True:
            prediction = models.Prediction(
                uuid=prediction_id,
                deployment_id=deployment_id,
                request_body=None,
                response_body=None,
            )
        else:
            prediction = models.Prediction(
                uuid=prediction_id,
                deployment_id=deployment_id,
            )

        self.session.add(prediction)
        self.session.commit()
