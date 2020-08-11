# -*- coding: utf-8 -*-
"""Shared functions."""
import random
import uuid
import re

from werkzeug.exceptions import NotFound
from sqlalchemy import asc, desc, text
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


def raise_if_operator_does_not_exist(operator_id):
    """Raises an exception if the specified operator does not exist.

    Args:
        operator_id (str): the operator uuid.
    """
    exists = db_session.query(Operator.uuid) \
        .filter_by(uuid=operator_id) \
        .scalar() is not None

    if not exists:
        raise NotFound("The specified operator does not exist")


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


def text_to_list(text):
    order_by = []
    regex = re.compile('\[(.*?)\]|(\S+)')
    matches = regex.finditer(text)
    for match in matches:
        if (match.group(1) is None):
            order_by.append(match.group(2))
        else:
            order_by.append(match.group(1))
    return order_by


def ordination_pagination(query, page_size, page, order_by, column):
    if order_by:
        order = text_to_list(order_by)
        if page != 0:
            if order[1]:
                if 'asc' == order[1].lower():
                    query = query.order_by(asc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
                if 'desc' == order[1].lower():
                    query = query.order_by(asc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
        else:
            if order[1]:
                if 'asc' == order[1].lower():
                    query = query.order_by(asc(text({order[0]})))
                if 'desc' == order[1].lower():
                    query = query.order_by(desc(text(order[0])))
    if page:
        query = query.order_by(text(column)).limit(page_size).offset((page - 1) * page_size)
    else:
        query = query.order_by(text(column))
    return query.all()
