# -*- coding: utf-8 -*-
"""Deployment Response controller."""
import os
import uuid

import pandas as pd
import requests

from projects import models
from projects.controllers.utils import uuid_alpha

BROKER_URL = os.getenv("BROKER_URL", "http://default-broker.anonymous.svc.cluster.local")


class ResponseController:
    def __init__(self, session):
        self.session = session

    def create_response(self, project_id: str, deployment_id: str, body: dict):
        """
        Creates a response entry in logs file.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        body : dict
        """
        if "data" in body:
            ndarray = pd.DataFrame(body["data"]["ndarray"])
            if "names" in body["data"]:
                names = body["data"]["names"]
                ndarray.columns = names
            body = ndarray.to_dict(orient="records")

        if isinstance(body, dict):
            body = [body]

        responses = []

        for record in body:
            responses.append(
                models.Response(
                    uuid=uuid_alpha(),
                    deployment_id=deployment_id,
                    body=record,
                )
            )

        self.session.bulk_save_objects(responses)
        self.session.commit()

        responses = self.session.query(models.Response) \
            .filter_by(deployment_id=deployment_id) \
            .order_by(models.Response.created_at.asc()) \
            .all()

        d = []

        if len(responses) > 0:
            for response in responses:
                d.append(response.body)

        data = pd.DataFrame(d)

        # sends latest data to broker
        response = requests.post(
            BROKER_URL,
            json={
                "data": {
                    "ndarray": data.values.tolist(),
                    "names": data.columns.tolist(),
                },
            },
            headers={
                "Ce-Id": str(uuid.uuid4()),
                "Ce-Specversion": "1.0",
                "Ce-Type": f"deployment.{deployment_id}",
                "Ce-Source": "logger.anonymous",
            },
        )
        response.raise_for_status()
