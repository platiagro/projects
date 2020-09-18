# -*- coding: utf-8 -*-
"""Experiments controller."""
import sys
from datetime import datetime
from os.path import join

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Dependency, Experiment, Template, Operator
from ..object_storage import remove_objects
from .tasks import get_tasks_by_tag
from .dependencies import create_dependency
from .operators import create_operator
from .utils import raise_if_project_does_not_exist, uuid_alpha


NOTFOUND = NotFound("The specified experiment does not exist")


def list_experiments(project_id):
    """Lists all experiments under a project.

    Args:
        project_id (str): the project uuid.

    Returns:
        A list of all experiments.
    """
    raise_if_project_does_not_exist(project_id)

    experiments = db_session.query(Experiment) \
        .filter_by(project_id=project_id) \
        .order_by(Experiment.position.asc()) \
        .all()
    return [experiment.as_dict() for experiment in experiments]


def create_experiment(name=None, project_id=None, copy_from=None):
    """Creates a new experiment in our database and adjusts the position of others.

    The new experiment is added to the end of the experiment list.

    Args:
        name (str): the experiment name.
        project_id (str): the project uuid.
        copy_from (str): the copy_from uuid.
    Returns:
        The experiment info.
    """
    raise_if_project_does_not_exist(project_id)

    if not isinstance(name, str):
        raise BadRequest("name is required")

    check_experiment_name = db_session.query(Experiment)\
        .filter(Experiment.project_id == project_id)\
        .filter(Experiment.name == name)\
        .first()
    if check_experiment_name:
        raise BadRequest("an experiment with that name already exists")

    experiment = Experiment(uuid=uuid_alpha(),
                            name=name,
                            project_id=project_id)
    db_session.add(experiment)
    db_session.commit()
    if copy_from:
        try:
            experiment_find = find_by_experiment_id(experiment_id=copy_from)
            """experiment_find = order_by_dependence(experiment_find)"""
            for operator in experiment_find['operators']:
                kwargs = {
                    "task_id": operator.task_id,
                    "parameters": operator.parameters,
                    "dependencies": operator.dependencies,
                    "position_x": operator.position_x,
                    "position_y": operator.position_y
                }
                create_operator(project_id, experiment.uuid, **kwargs)
        except Exception:
            delete_experiment(experiment.uuid, project_id)
            raise BadRequest('The experiment could not be duplicated')

    fix_positions(project_id=project_id,
                  experiment_id=experiment.uuid,
                  new_position=sys.maxsize)  # will add to end of list

    return experiment.as_dict()


def get_experiment(uuid, project_id):
    """Details an experiment from our database.

    Args:
        uuid (str): the experiment uuid to look for in our database.
        project_id (str): the project uuid.

    Returns:
        The experiment info.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NOTFOUND

    return experiment.as_dict()


def update_experiment(uuid, project_id, **kwargs):
    """Updates an experiment in our database and adjusts the position of others.

    Args:
        uuid (str): the experiment uuid to look for in our database.
        project_id (str): the project uuid.
        **kwargs: arbitrary keyword arguments.
    Returns:
        The experiment info.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NOTFOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != experiment.name:
            check_experiment_name = db_session.query(Experiment)\
                .filter(Experiment.project_id == project_id)\
                .filter(Experiment.name == name)\
                .first()
            if check_experiment_name:
                raise BadRequest("an experiment with that name already exists")

    # updates operators
    if "template_id" in kwargs:
        template_id = kwargs["template_id"]
        del kwargs["template_id"]
        template = Template.query.get(template_id)

        if template is None:
            raise BadRequest("The specified template does not exist")

        # remove dependencies
        operators = db_session.query(Operator).filter(Operator.experiment_id == uuid).all()
        for operator in operators:
            Dependency.query.filter(Dependency.operator_id == operator.uuid).delete()
        # remove operators
        Operator.query.filter(Operator.experiment_id == uuid).delete()

        # save the last operator id created to create dependency on next operator
        last_operator_id = None
        for task_id in template.tasks:
            operator_id = uuid_alpha()
            objects = [
                Operator(uuid=operator_id,
                         experiment_id=uuid,
                         task_id=task_id)
            ]
            db_session.bulk_save_objects(objects)
            if last_operator_id is not None:
                create_dependency(operator_id, last_operator_id)
            last_operator_id = operator_id

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


def delete_experiment(uuid, project_id):
    """Delete an experiment in our database and in the object storage.

    Args:
        uuid (str): the experiment uuid to look for in our database.
        project_id (str): the project uuid.

    Returns:
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(uuid)

    if experiment is None:
        raise NOTFOUND

    # remove dependencies
    operators = db_session.query(Operator).filter(Operator.experiment_id == uuid).all()
    for operator in operators:
        Dependency.query.filter(Dependency.operator_id == operator.uuid).delete()
    # remove operators
    Operator.query.filter(Operator.experiment_id == uuid).delete()

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
        .filter(Experiment.uuid != experiment_id)\
        .order_by(Experiment.position.asc())\
        .all()

    if experiment_id is not None:
        experiment = Experiment.query.get(experiment_id)
        other_experiments.insert(new_position, experiment)

    for index, experiment in enumerate(other_experiments):
        data = {"position": index}
        is_last = (index == len(other_experiments) - 1)
        # if experiment_id WAS NOT informed, then set the higher position as is_active=True
        if experiment_id is None and is_last:
            data["is_active"] = True
        # if experiment_id WAS informed, then set experiment.is_active=True
        elif experiment_id is not None and experiment_id == experiment.uuid:
            data["is_active"] = True
        else:
            data["is_active"] = False

        db_session.query(Experiment).filter_by(uuid=experiment.uuid).update(data)
    db_session.commit()


def find_by_experiment_id(experiment_id):
    """Search the experiment by id
    Args:
        experiment_id (str): the experiment uuid

    Returns:
        List of experiment
    """
    experiment = Experiment.query.get(experiment_id)

    if experiment is None:
        raise NOTFOUND

    return experiment.as_dict()
