# -*- coding: utf-8 -*-
"""Shared functions."""
import random
import re
import uuid

from werkzeug.exceptions import NotFound
from kfp_server_api.exceptions import ApiException

from projects.database import db_session
from projects.kfp import KFP_CLIENT
from projects.models import Deployment, Experiment, Operator, Project, Task


def raise_if_task_does_not_exist(task_id):
    """
    Raises an exception if the specified task does not exist.

    Parameters
    ----------
    task_id : str

    Raises
    ------
    NotFound
    """
    exists = db_session.query(Task.uuid) \
        .filter_by(uuid=task_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified task does not exist")


def raise_if_project_does_not_exist(project_id):
    """
    Raises an exception if the specified project does not exist.

    Parameters
    ----------
    project_id :str

    Raises
    ------
    NotFound
    """
    exists = db_session.query(Project.uuid) \
        .filter_by(uuid=project_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified project does not exist")


def raise_if_experiment_does_not_exist(experiment_id):
    """
    Raises an exception if the specified experiment does not exist.

    Parameters
    ----------
    experiment_id : str

    Raises
    ------
    NotFound
    """
    exists = db_session.query(Experiment.uuid) \
        .filter_by(uuid=experiment_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified experiment does not exist")


def raise_if_deployment_does_not_exist(deployment_id):
    """
    Raises an exception if the specified deployment does not exist.

    Parameters
    ----------
    deployment_id : str

    Raises
    ------
    NotFound
    """
    exists = db_session.query(Deployment.uuid) \
        .filter_by(uuid=deployment_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified deployment does not exist")


def raise_if_operator_does_not_exist(operator_id, experiment_id=None):
    """
    Raises an exception if the specified operator does not exist.

    Parameters
    ----------
    operator_id : str
    experiment_id : str

    Raises
    ------
    NotFound
    """
    operator = db_session.query(Operator) \
        .filter_by(uuid=operator_id)

    if operator.scalar() is None:
        raise NotFound("The specified operator does not exist")
    else:
        # verify if operator is from the provided experiment
        if experiment_id and operator.one().as_dict()["experimentId"] != experiment_id:
            raise NotFound("The specified operator is from another experiment")


def raise_if_run_does_not_exist(run_id):
    """
    Raises an exception if the specified run does not exist.

    Parameters
    ----------
    run_id : str

    Raises
    ------
    NotFound
    """
    try:
        KFP_CLIENT.get_run(run_id=run_id)
    except ApiException:
        raise NotFound("The specified run does not exist")


def uuid_alpha():
    """
    Generates an uuid that always starts with an alpha char.

    Returns
    -------
    str
    """
    uuid_ = str(uuid.uuid4())
    if not uuid_[0].isalpha():
        c = random.choice(["a", "b", "c", "d", "e", "f"])
        uuid_ = f"{c}{uuid_[1:]}"
    return uuid_


def list_objects(list_object):
    """
    Extracting uuids from informed json.

    Parameters
    ----------
    list_object : list
        String containing the project's uuid.

    Returns
    -------
    list
        All uuids.
    """
    all_projects_ids = []
    for i in list_object:
        all_projects_ids.append(i["uuid"])
    return all_projects_ids


def objects_uuid(list_object):
    """
    Recovering uuids from information projects.

    Parameters
    ----------
    list_object : lits
        List of project ids.

    Returns
    -------
    list
        All uuids.
    """
    uuids = []
    for i in list_object:
        uuids.append(i.uuid)
    return uuids


def text_to_list(order):
    """
    Turn text into list.

    Parameters
    ----------
    order : str
        Column name and order.

    Returns
    -------
    list
    """
    order_by = []
    regex = re.compile(r"\[(.*?)\]|(\S+)")
    matches = regex.finditer(order)
    for match in matches:
        order_by.append(match.group(2)) if match.group(1) is None else order_by.append(match.group(1))
    return order_by
