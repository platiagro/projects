# -*- coding: utf-8 -*-
"""Shared functions."""
import random
import uuid
import re

from werkzeug.exceptions import NotFound

from projects.database import db_session
from projects.models import Experiment, Operator, Project, Task


def raise_if_task_does_not_exist(task_id):
    """Raises an exception if the specified task does not exist.

    Args:
        task_id (str): the task uuid.
    """
    exists = db_session.query(Task.uuid) \
        .filter_by(uuid=task_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified task does not exist")


def raise_if_project_does_not_exist(project_id):
    """Raises an exception if the specified project does not exist.

    Args:
        project_id (str): the project uuid.
    """
    exists = db_session.query(Project.uuid) \
        .filter_by(uuid=project_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified project does not exist")


def raise_if_experiment_does_not_exist(experiment_id):
    """Raises an exception if the specified experiment does not exist.

    Args:
        experiment_id (str): the experiment uuid.
    """
    exists = db_session.query(Experiment.uuid) \
        .filter_by(uuid=experiment_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified experiment does not exist")


def raise_if_operator_does_not_exist(operator_id, experiment_id=None):
    """Raises an exception if the specified operator does not exist.

    Args:
        operator_id (str): the operator uuid.
    """
    operator = db_session.query(Operator) \
        .filter_by(uuid=operator_id)

    if operator.scalar() is None:
        raise NotFound("The specified operator does not exist")
    else:
        # verify if operator is from the provided experiment
        if experiment_id and operator.one().as_dict()["experimentId"] != experiment_id:
            raise NotFound("The specified operator is from another experiment")


def uuid_alpha() -> str:
    """Generates an uuid that always starts with an alpha char."""
    uuid_ = str(uuid.uuid4())
    if not uuid_[0].isalpha():
        c = random.choice(["a", "b", "c", "d", "e", "f"])
        uuid_ = f"{c}{uuid_[1:]}"
    return uuid_


def pagination_datasets(page, page_size, dataset):
    """pagination of datasets.

    Args:
        page_size(int) : record numbers
        page(int): page number
        dataset(json): data to be paged

    Returns:
        Paged dataset

    """
    try:
        count = 0
        new_datasets = []
        total_elements = len(dataset['data'])
        page = (page * page_size) - page_size
        for i in range(page, total_elements):
            new_datasets.append(dataset['data'][i])
            count += 1
            if page_size == count:
                response = {
                    'columns': dataset['columns'],
                    'data': new_datasets,
                    'total': len(dataset['data'])
                }
                return response
        if len(new_datasets) == 0:
            raise NotFound("The informed page does not contain records")
        else:
            response = {
                'columns': dataset['columns'],
                'data': new_datasets,
                'total': len(dataset['data'])
            }
            return response
    except RuntimeError:
        raise NotFound("The specified page does not exist")


def list_objects(list_object):
    """Extracting uuids from informed json.

    Args:
        list_object(json): string containing the project's uuid

    Returns:
        all uuids

    """
    all_projects_ids = []
    for i in list_object:
        all_projects_ids.append(i['uuid'])
    return all_projects_ids


def objects_uuid(list_object):
    """Recovering uuids from information projects.

    Args:
        list_object(projects): list of projects

    Returns:
        all uuids

    """
    uuids = []
    for i in list_object:
        uuids.append(i.uuid)
    return uuids


def text_to_list(order):
    """Turn text into list.

    Args:
        order(str): column name and order

    Returns:
        list

    """
    order_by = []
    regex = re.compile(r'\[(.*?)\]|(\S+)')
    matches = regex.finditer(order)
    for match in matches:
        order_by.append(match.group(2)) if match.group(1) is None else order_by.append(match.group(1))
    return order_by
