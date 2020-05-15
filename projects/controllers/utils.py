# -*- coding: utf-8 -*-
"""Shared functions."""
import random
import string
import uuid

from werkzeug.exceptions import NotFound

from ..database import db_session
from ..models import Component, Experiment, Project


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


def uuid_alpha() -> str:
    """Generates an uuid that always starts with an alpha char."""
    uuid_ = str(uuid.uuid4())
    if not uuid_[0].isalpha():
        c = random.choice(string.ascii_lowercase)
        uuid_ = f"{c}{uuid_[1:]}"
    return uuid_
