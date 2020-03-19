# -*- coding: utf-8 -*-
"""Experiments controller."""
import sys
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
    return sorted([experiment.as_dict() for experiment in experiments], key=lambda e: e["position"])


def create_experiment(name=None, project_id=None, dataset=None, target=None,
                      **kwargs):
    """Creates a new experiment in our database and adjusts the position of others.

    The new experiment is added to the end of the experiment list.

    Args:
        name (str): the experiment name.
        project_id (str): the project uuid.
        dataset (str, optional): the dataset uuid.
        target (str, optional): the target column.

    Returns:
        The experiment info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    experiment = Experiment(uuid=str(uuid4()),
                            name=name,
                            project_id=project_id,
                            dataset=dataset,
                            target=target,
                            position=-1)    # use temporary position -1, fix_position below
    db_session.add(experiment)
    db_session.commit()

    fix_positions(project_id=project_id,
                  experiment_id=experiment.uuid,
                  new_position=sys.maxsize)  # will add to end of list
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
    """Updates an experiment in our database and adjusts the position of others.

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

    fix_positions(project_id=experiment.project_id,
                  experiment_id=experiment.uuid,
                  new_position=experiment.position)

    return experiment.as_dict()


def delete_experiment(uuid):
    """Delete an experiment in our database and in the object storage.

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

    fix_positions(project_id=experiment.project_id)

    prefix = join("experiments", uuid)
    remove_objects(prefix=prefix)

    return {"message": "Experiment deleted"}


def fix_positions(project_id, experiment_id=None, new_position=None):
    """Reorders the experiments in a project when an experiment is updated/deleted.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        new_position (int): the position where the experiment is shown.
    """
    other_experiments = db_session.query(Experiment) \
        .filter_by(project_id=project_id) \
        .filter(Experiment.uuid != experiment_id).all()

    if experiment_id is not None:
        experiment = Experiment.query.get(experiment_id)
        other_experiments.insert(new_position, experiment)

    for index, experiment in enumerate(other_experiments):
        data = {"position": index}
        db_session.query(Experiment).filter_by(uuid=experiment.uuid).update(data)
    db_session.commit()
