# -*- coding: utf-8 -*-
"""Experiments components controller."""
from uuid import uuid4

from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import ExperimentComponent


def list_components(project_id, experiment_id):
    """Lists all components under an experiment.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.

    Returns:
        A list of all components ids.
    """
    experiment_components = ExperimentComponent.query.filter_by(experiment_id=experiment_id)
    return [component.as_dict() for component in experiment_components]


def create_component(project_id, experiment_id, component_id=None,
                     position=None, **kwargs):
    """Creates a new component in our database.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        component_id (str): the component uuid.
        position (int, optional): the position where the component is shown.

    Returns:
        The component info.
    """
    if not isinstance(component_id, str):
        raise BadRequest("componentId is required")

    if not isinstance(position, int):
        raise BadRequest("position is required")

    experiment_component = ExperimentComponent(uuid=str(uuid4()),
                                               experiment_id=experiment_id,
                                               component_id=component_id,
                                               position=position)
    db_session.add(experiment_component)
    db_session.commit()
    return experiment_component.as_dict()


def delete_component(uuid):
    """Delete a component in our database.

    Args:
        uuid (str): the experiment_component uuid to look for in our database.

    Returns:
        The deletion result.
    """
    experiment_component = ExperimentComponent.query.get(uuid)

    if experiment_component is None:
        raise NotFound("The specified experiment-component does not exist")

    db_session.delete(experiment_component)
    db_session.commit()

    return {"message": "Component deleted"}
