# -*- coding: utf-8 -*-
"""Experiments controller."""
from datetime import datetime
from os.path import join
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Experiment
from ..object_storage import remove_objects


def list_experiments(project_id):
    """Lists all experiments under a project.

    Args:
        project_id (str): the project uuid.

    Returns:
        A list of all experiments ids.
    """
    experiments = db_session.query(Experiment).filter_by(project_id=project_id).all()
    return [experiment.uuid for experiment in experiments]


def create_experiment(name=None, project_id=None, dataset=None, target=None,
                      position=None, **kwargs):
    """Creates a new experiment in our database.

    Args:
        name (str): the experiment name.
        project_id (str): the project uuid.
        dataset (str, optional): the dataset uuid.
        target (str, optional): the target column.
        position (int, optional): the position where the experiment is shown.

    Returns:
        The experiment info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    experiment = Experiment(uuid=str(uuid4()), name=name, project_id=project_id,
                            dataset=dataset, target=target, position=position)
    db_session.add(experiment)
    db_session.commit()
    return experiment.as_dict()


def get_experiment(uuid):
    """Details an experiment from our database.

    Args:
        uuid (str): the experiment uuid to look for in our database.

    Returns:
        The experiment info.
    """
    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NotFound("The specified experiment does not exist")

    return experiment.as_dict()


def update_experiment(uuid, **kwargs):
    """Updates an experiment in our database.

    Args:
        uuid (str): the experiment uuid to look for in our database.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The experiment info.
    """
    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NotFound("The specified experiment does not exist")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Experiment).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return experiment.as_dict()


def delete_experiment(uuid):
    """Delete an experiment in our database.

    Args:
        uuid (str): the experiment uuid to look for in our database.

    Returns:
        The deletion result.
    """
    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NotFound("The specified experiment does not exist")

    db_session.delete(experiment)
    db_session.commit()

    prefix = join("experiments", uuid)
    remove_objects(prefix=prefix)

    return {"message": "Experiment deleted"}
