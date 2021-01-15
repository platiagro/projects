# -*- coding: utf-8 -*-
"""Deployments controller."""
import sys
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.deployments.runs import create_run, terminate_run
from projects.controllers.experiments import list_experiments
from projects.controllers.operators import create_operator
from projects.controllers.utils import raise_if_project_does_not_exist, \
    uuid_alpha
from projects.database import db_session
from projects.kfp.deployments import get_deployment_runs
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


def create_deployment(project_id,
                      experiments=None,
                      template_id=None):
    """
    Creates new deployments in our database and adjusts the position of others.

    Parameters
    ----------
    project_id : str
    experiments : list
        A list of experiment ids to be copied to deployments.
    template_id : str
    Returns
    -------
    dict
        The deployment attributes.

    Raises
    ------
    NotFound
        When project_id does not exist.
    BadRequest
        When any experiment does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    if template_id is not None:
        raise BadRequest("templateId is not implemented yet")

    if not experiments:
        raise BadRequest("experiments were not specified")

    experiments_dict = {e["uuid"]: e for e in list_experiments(project_id=project_id)}

    for experiment_id in experiments:
        if experiment_id not in experiments_dict:
            raise BadRequest("some experiments do not exist")

    deployments = []

    for experiment_id in experiments:
        experiment = experiments_dict[experiment_id]

        deployment = Deployment(uuid=uuid_alpha(),
                                experiment_id=experiment_id,
                                name=experiment["name"],
                                project_id=project_id)
        db_session.add(deployment)
        db_session.flush()

        deployments.append(deployment)

        copy_operators(project_id=project_id,
                       experiment_id=experiment_id,
                       deployment_id=deployment.uuid)

        fix_positions(project_id=project_id,
                      deployment_id=deployment.uuid,
                      new_position=sys.maxsize)  # will add to end of list

    db_session.commit()

    # Temporary: also run deployment (while web-ui isn't ready)
    for deployment in deployments:
        create_run(project_id=project_id,
                   deployment_id=deployment.uuid)

    return [deployment.as_dict() for deployment in deployments]


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
    deployment_details = get_deployment_runs(deployment_id)

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

    # Temporary: also delete run deployment (while web-ui isn't ready)
    terminate_run(
        project_id=project_id,
        deployment_id=deployment_id,
        run_id='latest'
    )

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


def copy_operators(project_id, experiment_id, deployment_id):
    """
    Copies the operators from an experiment to a deployment.
    Creates new uuids and don't keep the experiment_id relationship.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    deployment_id : str
    """
    operators = db_session.query(Operator) \
        .filter_by(experiment_id=experiment_id) \
        .order_by(Operator.dependencies.asc()) \
        .all()

    operators_mapper = {}

    for operator in operators:
        dependencies = []

        if operator.dependencies:
            # Get the new id's of the dependencies
            dependencies = [operators_mapper[dependencie_uuid] for dependencie_uuid in operator.dependencies]

        operator_ = create_operator(deployment_id=deployment_id,
                                    project_id=project_id,
                                    task_id=operator.task_id,
                                    parameters=operator.parameters,
                                    dependencies=dependencies,
                                    position_x=operator.position_x,
                                    position_y=operator.position_y)

        # Keys is the old uuid and values the new one
        operators_mapper.update({operator.uuid: operator_["uuid"]})

    db_session.commit()
