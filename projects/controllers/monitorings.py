# -*- coding: utf-8 -*-
"""Monitorings controller."""
from werkzeug.exceptions import NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist, raise_if_task_does_not_exist, \
    uuid_alpha
from projects.database import db_session
from projects.models import Monitoring


NOT_FOUND = NotFound("The specified monitoring does not exist")


def list_monitorings(project_id, deployment_id):
    """Lists all monitorings under a deployment.
    Args:
        project_id (str): the project uuid.
        deployment_id (str): the deployment uuid.
    Returns:
        A list of all monitorings.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    monitorings = db_session.query(Monitoring) \
        .filter_by(deployment_id=deployment_id) \
        .order_by(Monitoring.created_at.asc()) \
        .all()

    return [monitoring.as_dict() for monitoring in monitorings]


def create_monitoring(project_id,
                      deployment_id=None,
                      task_id=None):
    """Creates a new monitoring in our database.
    Args:
        project_id (str): the project uuid.
        deployment_id (str): the deployment uuid.
        task_id (str): the task uuid.
    Returns:
        The monitoring info.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)
    raise_if_task_does_not_exist(task_id)

    monitoring = Monitoring(
        uuid=uuid_alpha(),
        deployment_id=deployment_id,
        task_id=task_id
    )
    db_session.add(monitoring)
    db_session.commit()
    return monitoring.as_dict()


def delete_monitoring(uuid, project_id, deployment_id):
    """Delete a monitoring in our database.
    Args:
        uuid (str): the monitoring uuid to look for in our database.
        project_id (str): the project uuid.
        deployment_id (str): the deployment uuid.
    Returns:
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    monitoring = Monitoring.query.get(uuid)

    if monitoring is None:
        raise NOT_FOUND

    db_session.delete(monitoring)
    db_session.commit()

    return {"message": "Monitoring deleted"}
