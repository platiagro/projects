# -*- coding: utf-8 -*-
"""Training history controller."""
from schema import Schema, SchemaError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import TrainingHistory
from .utils import raise_if_project_does_not_exist, raise_if_experiment_does_not_exist, \
    uuid_alpha

NOT_FOUND = NotFound("The specified training history does not exist")

operator_schema = Schema({
    'operatorId': str,
    'taskId': str,
    'parameters': list,
})


def list_training_history(project_id, experiment_id):
    """Lists all training history under an experiment.
    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
    Returns:
        A list of all training history.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    training_histories = db_session.query(TrainingHistory) \
        .filter_by(experiment_id=experiment_id) \
        .order_by(TrainingHistory.created_at.desc()) \
        .all()

    return [training_history.as_dict() for training_history in training_histories]


def create_training_history(project_id, experiment_id, run_id=None, operators=None, **kwargs):
    """Creates a new training history in our database.
    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        run_id (str): the run id.
        operators (list): the operators details used in training.
        **kwargs: arbitrary keyword arguments.
    Returns:
        The training history info.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    if run_id is None:
        raise BadRequest('Run id can not be null.')

    for operator in operators:
        if not validate_operator(operator):
            raise BadRequest('Invalid operator in request.')

    training_history = TrainingHistory(uuid=uuid_alpha(),
                                       project_id=project_id,
                                       experiment_id=experiment_id,
                                       run_id=run_id,
                                       details=operators)
    db_session.add(training_history)
    db_session.commit()

    return training_history.as_dict()


def delete_training_history(uuid, project_id, experiment_id):
    """Delete a training history in our database.
    Args:
        uuid (str): the training history uuid to look for in our database.
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
    Returns:
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)

    training_history = TrainingHistory.query.get(uuid)

    if training_history is None:
        raise NOT_FOUND

    db_session.delete(training_history)
    db_session.commit()

    return {"message": "Training history deleted"}


def validate_operator(operator):
    try:
        operator_schema.validate(operator)
        return True
    except SchemaError:
        return False
