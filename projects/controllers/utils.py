# -*- coding: utf-8 -*-
"""Shared functions."""
import random
import uuid

from werkzeug.exceptions import NotFound

from ..database import db_session
from ..models import Component, Experiment, Operator, Project


def raise_if_component_does_not_exist(component_id):
    """Raises an exception if the specified component does not exist.

    Args:
        component_id (str): the component uuid.
    """
    exists = db_session.query(Component.uuid) \
        .filter_by(uuid=component_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified component does not exist")


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
        if experiment_id:
            if operator.one().as_dict()["experimentId"] != experiment_id:
                raise NotFound("The specified operator is from another experiment")


def uuid_alpha() -> str:
    """Generates an uuid that always starts with an alpha char."""
    uuid_ = str(uuid.uuid4())
    if not uuid_[0].isalpha():
        c = random.choice(["a", "b", "c", "d", "e", "f"])
        uuid_ = f"{c}{uuid_[1:]}"
    return uuid_


def pagination_datasets(page, page_size, elements):
    try:
        count = 0
        new_elements = []
        total_elements = len(elements['data'])
        """The numbers of items to return maximum 100 """
        if page_size > 100:
            page_size = 100
        page = (page * page_size) - page_size
        for i in range(page, total_elements):
            new_elements.append(elements['data'][i])
            count += 1
            if page_size == count:
                response = {
                    'columns': elements['columns'],
                    'data': new_elements,
                    'total': len(elements['data'])
                }
                return response
        if len(new_elements) == 0:
            raise NotFound("The informed page does not contain records")
        else:
            response = {
                'columns': elements['columns'],
                'data': new_elements,
                'total': len(elements['data'])
            }
            return response
    except RuntimeError:
        raise NotFound("The specified page does not exist")


def list_objects(list_object):
    all_projects_ids = []
    for i in list_object:
        all_projects_ids.append(i['uuid'])
    return all_projects_ids


def objects_uuid(list_object):
    ids = []
    for i in list_object:
        ids.append(i.uuid)
    return ids
