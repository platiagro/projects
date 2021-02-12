# -*- coding: utf-8 -*-
"""Logger controller."""
import os
import uuid

import pandas as pd
import requests

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
            body = ndarray.to_json(orient="records", lines=True)

        filename = f"{deployment_id}.txt"

        with open(filename, "a") as f:
            f.write(f"{body}\n")

        # sends latest data to broker
        data = pd.read_json(filename, lines=True)
        latest_data = data.values.tolist()

        response = requests.post(
            BROKER_URL,
            json={
                "data": {
                    "ndarray": latest_data,
                },
            },
            headers={
                "Ce-Id": str(uuid.uuid4()),
                "Ce-Specversion": "1.0",
                "Ce-Type": "logger.anonymous.request",
                "Ce-Source": "logger.anonymous",
            },
        )
        response.raise_for_status()
