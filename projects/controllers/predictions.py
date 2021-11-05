# -*- coding: utf-8 -*-
"""Predictions controller."""
import json
import logging
from typing import Optional

import requests
from platiagro import load_dataset

from projects import models, schemas
from projects.controllers.utils import (
    parse_dataframe_to_seldon_request,
    parse_file_buffer_to_seldon_request,
    uuid_alpha,
)
from projects.exceptions import BadRequest, NotFound
from projects.kubernetes.seldon import get_seldon_deployment_url

NOT_FOUND = NotFound("The specified prediction does not exist")


class PredictionController:
    def __init__(self, session, background_tasks=None):
        self.session = session
        self.background_tasks = background_tasks

    def create_prediction(
        self,
        deployment_id: str,
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
        prediction_as_schema: schemas.prediction.PredictionBase

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
            prediction_id=str(uuid_alpha()),
            deployment_id=deployment_id,
            request_body=request,
            response_body=None,
            status="started",
        )

        prediction_as_schema = schemas.PredictionBase.from_orm(prediction_object)

        url = get_seldon_deployment_url(deployment_id=deployment_id, external_url=False)
        self.background_tasks.add_task(
            self.start_and_save_seldon_prediction,
            request_body=request,
            prediction_object=prediction_object,
            url=url,
        )
        return prediction_as_schema

    def create_prediction_database_object(
        self,
        prediction_id: str,
        deployment_id: str,
        status: str,
        request_body: Optional[dict] = None,
        response_body: Optional[dict] = None,
    ):
        """
        Creates a prediction object in database.

        Parameters
        ----------
        prediction_id : str
        deployment_id : str
        request_body: dict
        response_body: dict

        Returns
        -------
        prediction: models.prediction.Prediction

        """
        prediction = models.Prediction(
            uuid=prediction_id,
            deployment_id=deployment_id,
            status=status,
            request_body=json.dumps(request_body),
            response_body=json.dumps(response_body),
        )

        self.session.add(prediction)
        self.session.commit()
        return prediction

    def start_and_save_seldon_prediction(self, request_body, prediction_object, url):
        """
        Makes a POST request in seldon API to start prediction and gets the result
        and updates the prediction object in database

        Parameters
        ----------
        request_body: dict
            request data to send as POST on seldon API
        prediction_object : models.prediction.Prediction
            prediction database object so that data can be updated in database
        url : str
            seldon API url to send the request as POST

        Returns
        -------

        """
        response = requests.post(url=url, json=request_body)
        if response.status_code == 200:
            prediction_object.status = "done"
        else:
            logging.info(f"Unable to acquire prediction data: {response._content}")
            prediction_object.status = "failed"

        prediction_object.response_body = response._content
        self.session.commit()

    def get_prediction(
        self,
        prediction_id,
    ):
        """
        Gets prediction from database by uuid and returns to client.

        Parameters
        ----------
        prediction_id: str

        Returns
        -------
        prediction_as_schema: schemas.prediction.Prediction

        Raises
        ------
        BadRequest
            When query doesn't find prediction in database with given ID.
        """
        prediction_orm_obj = self.session.query(models.Prediction).get(prediction_id)

        if not prediction_orm_obj:
            raise BadRequest(NOT_FOUND)

        predicton_as_schema = schemas.Prediction.from_orm(prediction_orm_obj)
        return predicton_as_schema
