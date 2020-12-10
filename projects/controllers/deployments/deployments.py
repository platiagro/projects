# -*- coding: utf-8 -*-
"""Deployments controller."""
import sys
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.operators import create_operator
from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist, uuid_alpha
from projects.database import db_session
from projects.kfp.utils import get_deployment_by_id
from projects.models import Deployment, Operator


NOT_FOUND = NotFound("The specified deployment does not exist")


def list_deployments(project_id):
    """
    Lists all deployments under a project.

    Parameters
    ----------
    project_id: str

    Returns
    -------
    list
        A list of all experiments.

    Raises
    ------
    NotFound
        When project_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    deployments = db_session.query(Deployment) \
        .filter_by(project_id=project_id) \
        .order_by(Deployment.position.asc()) \
        .all()

    return [deployment.as_dict() for deployment in deployments]


def create_deployment(project_id=None,
                      experiment_id=None,
                      is_active=None,
                      name=None,
                      operators=None,
                      position=None,
                      status=None):
    """
    Creates a new deployment in our database and adjusts the position of others.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    is_active : bool
        Whether deployment is active.
    name : str
    operators : list
        The deployment operators.
    position : int
        The deployment position.

    Returns
    -------
    dict
        The deployment attributes.

    Raises
    ------
    NotFound
        When project_id does not exist.
    BadRequest
        When name is not a str instance.
        When name is already the name of another deployment.
    """
    raise_if_project_does_not_exist(project_id)

    if not isinstance(name, str):
        raise BadRequest("name is required")

    check_deployment_name = db_session.query(Deployment) \
        .filter(Deployment.project_id == project_id) \
        .filter(Deployment.name == name) \
        .first()
    if check_deployment_name:
        raise BadRequest("a deployment with that name already exists")

    deployment = Deployment(uuid=uuid_alpha(),
                            experiment_id=experiment_id,
                            is_active=is_active,
                            name=name,
                            project_id=project_id)
    db_session.add(deployment)

    if operators and len(operators) > 0:
        for operator in operators:
            create_operator(deployment_id=deployment.uuid,
                            project_id=project_id,
                            task_id=operator.get("taskId"),
                            parameters=operator.get("parameters"),
                            dependencies=operator.get("dependencies"),
                            position_x=operator.get("positionX"),
                            position_y=operator.get("positionY"))
    db_session.commit()

    if position is None:
        position = sys.maxsize  # will add to end of list
    fix_positions(project_id=project_id, deployment_id=deployment.uuid, new_position=position)

    return deployment.as_dict()


def get_deployment(project_id, deployment_id):
    """
    Details a deployment from our database.

    Parameters
    ----------
    project_id : str
    deployment_id : str

    Returns
    -------
    dict
        The deployment attributes.

    Raises
    ------
    NotFound
        When either project_id or deployment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    deployment = Deployment.query.get(deployment_id)
    if deployment is None:
        raise NOT_FOUND

    resp = deployment.as_dict()
    deployment_details = get_deployment_by_id(deployment_id)

    if not deployment_details:
        return resp

    resp["deployedAt"] = deployment_details["createdAt"]
    resp["runId"] = deployment_details["runId"]
    resp["status"] = deployment_details["status"]
    resp["url"] = deployment_details["url"]

    return resp


def update_deployment(project_id, deployment_id, **kwargs):
    """
    Updates a deployment in our database and adjusts the position of others.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The deployment attributes.

    Raises
    ------
    NotFound
        When either project_id or deployment_id does not exist.
    BadRequest
        When name is already the name of another deployment.
    """
    raise_if_project_does_not_exist(project_id)

    deployment = Deployment.query.get(deployment_id)

    if deployment is None:
        raise NOT_FOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != deployment.name:
            check_deployment_name = db_session.query(Deployment) \
                .filter(Deployment.project_id == project_id) \
                .filter(Deployment.name == name) \
                .first()
            if check_deployment_name:
                raise BadRequest("a deployment with that name already exists")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Deployment).filter_by(uuid=deployment_id).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    fix_positions(project_id=deployment.project_id,
                  deployment_id=deployment.uuid,
                  new_position=deployment.position)

    return deployment.as_dict()


def delete_deployment(project_id, deployment_id):
    """
    Delete a deployment in our database and in the object storage.

    Parameters
    ----------
    project_id: str
    deployment_id : str

    Raises
    ------
    NotFound
        When either project_id or deployment_id does not exist.

    Returns
    -------
    dict
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)

    deployment = Deployment.query.get(deployment_id)

    if deployment is None:
        raise NOT_FOUND

    # remove operators
    Operator.query.filter(Operator.deployment_id == deployment_id).delete()

    db_session.delete(deployment)
    db_session.commit()

    fix_positions(project_id=project_id)

    return {"message": "Deployment deleted"}


def fix_positions(project_id, deployment_id=None, new_position=None):
    """
    Reorders the deployments in a project when a deployment is updated/deleted.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    new_position : int
        The position where the experiment is shown.
    """
    other_deployments = db_session.query(Deployment) \
        .filter_by(project_id=project_id) \
        .filter(Deployment.uuid != deployment_id) \
        .order_by(Deployment.position.asc()) \
        .all()

    if deployment_id is not None:
        deployment = Deployment.query.get(deployment_id)
        other_deployments.insert(new_position, deployment)

    for index, deployment in enumerate(other_deployments):
        data = {"position": index}
        is_last = (index == len(other_deployments) - 1)
        # if deployment_id WAS NOT informed, then set the higher position as is_active=True
        if deployment_id is None and is_last:
            data["is_active"] = True
        # if deployment_id WAS informed, then set experiment.is_active=True
        elif deployment_id is not None and deployment_id == deployment.uuid:
            data["is_active"] = True
        else:
            data["is_active"] = False

        db_session.query(Deployment).filter_by(uuid=deployment.uuid).update(data)
    db_session.commit()
