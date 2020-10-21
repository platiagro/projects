# -*- coding: utf-8 -*-
"""Compare results controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import CompareResult
from .utils import raise_if_project_does_not_exist, raise_if_experiment_does_not_exist, \
    uuid_alpha


NOT_FOUND = NotFound("The specified compare result does not exist")


def list_compare_results(project_id):
    """Lists all compare results under a project.
    Args:
        project_id (str): the project uuid.
    Returns:
        A list of all compare results.
    """
    raise_if_project_does_not_exist(project_id)

    compare_results = db_session.query(CompareResult) \
        .filter_by(project_id=project_id) \
        .order_by(CompareResult.created_at.asc()) \
        .all()

    return [compare_result.as_dict() for compare_result in compare_results]


def create_compare_result(project_id=None):
    """Creates a new compare result in our database.
    Args:
        project_id (str): the project uuid.
    Returns:
        The compare result info.
    """
    raise_if_project_does_not_exist(project_id)

    compare_result = CompareResult(uuid=uuid_alpha(), project_id=project_id)
    db_session.add(compare_result)
    db_session.commit()

    return compare_result.as_dict()


def update_compare_result(uuid, project_id, **kwargs):
    """Updates a compare result in our database.
    Args:
        uuid (str): the a compare result uuid to look for in our database.
        project_id (str): the project uuid.
        **kwargs: arbitrary keyword arguments.
    Returns:
        The compare result info.
    """
    raise_if_project_does_not_exist(project_id)

    compare_result = CompareResult.query.get(uuid)

    if compare_result is None:
        raise NOT_FOUND

    experiment_id = kwargs.get("experiment_id", None)
    if experiment_id:
        raise_if_experiment_does_not_exist(experiment_id)

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(CompareResult).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return compare_result.as_dict()


def delete_compare_result(uuid, project_id):
    """Delete a compare result in our database.
    Args:
        uuid (str): the compare result uuid to look for in our database.
        project_id (str): the project uuid.
    Returns:
        The deletion result.
    """
    raise_if_project_does_not_exist(project_id)

    compare_result = CompareResult.query.get(uuid)

    if compare_result is None:
        raise NOT_FOUND

    db_session.delete(compare_result)
    db_session.commit()

    return {"message": "Compare result deleted"}
