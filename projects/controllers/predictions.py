# -*- coding: utf-8 -*-
"""Predictions controller."""
from json import loads

import requests
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from projects.controllers.utils import uuid_alpha, parse_csv_buffer_to_seldon_request, \
    raise_if_deployment_does_not_exist, raise_if_project_does_not_exist
from projects.database import db_session
from projects.kubernetes.seldon import get_seldon_deployment_url
from projects.models import Prediction

def list_predictions():
    """
    List all predictions from our database.

    Returns
    -------
    list
        A list of all predictions.
    """
    predictions = db_session.query(Prediction).all()

    return predictions


def create_prediction(project_id=None, deployment_id=None, file=None):
    """
    Creates a new prediction in our database.    print(request)

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
    raise_if_project_does_not_exist(project_id)

    #raise_if_deployment_does_not_exist(deployment_id)

    if not isinstance(file, FileStorage):
        raise BadRequest("`file` is required.")

    url = get_seldon_deployment_url(deployment_id)
    request = parse_csv_buffer_to_seldon_request(file)
    response = requests.post(url, json=request)

    prediction = Prediction(uuid=uuid_alpha())
    db_session.commit() 
    db_session.add(prediction)

    return loads(response._content)
