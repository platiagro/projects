# -*- coding: utf-8 -*-
"""Comparison controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist, uuid_alpha
from projects.database import db_session
from projects.models import Comparison


NOT_FOUND = NotFound("The specified comparison does not exist")


def list_comparisons(project_id):
    """
    Lists all comparisons under a project.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    list
        A list of all comparisons.

    Raises
    ------
    NotFound
        When project_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    comparisons = db_session.query(Comparison) \
        .filter_by(project_id=project_id) \
        .order_by(Comparison.created_at.asc()) \
        .all()

    return [comparison.as_dict() for comparison in comparisons]


def create_comparison(project_id=None):
    """
    Creates a new comparison in our database.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    dict
        The comparison attributes.

    Raises
    ------
    NotFound
        When project_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    comparison = Comparison(uuid=uuid_alpha(), project_id=project_id)
    db_session.add(comparison)
    db_session.commit()

    return comparison.as_dict()


def update_comparison(project_id, comparison_id, **kwargs):
    """
    Updates a comparison in our database.

    Parameters
    ----------
    project_id : str
    comparison_id : str
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The comparison attributes.

    Raises
    ------
    BadRequest
        When the `**kwargs` (comparison attributes) are invalid.
    NotFound
        When either project_id or comparison_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    comparison = Comparison.query.get(comparison_id)

    if comparison is None:
        raise NOT_FOUND

    experiment_id = kwargs.get("experiment_id", None)
    if experiment_id:
        raise_if_experiment_does_not_exist(experiment_id)

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Comparison) \
            .filter_by(uuid=comparison_id) \
            .update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return comparison.as_dict()


def delete_comparison(project_id, comparison_id):
    """
    Delete a comparison in our database.

    Parameters
    ----------
    project_id : str
    comparison_id : str

    Returns
    -------
    dict
        The deletion result.

    Raises
    ------
    NotFound
        When either project_id or comparison_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)

    comparison = Comparison.query.get(comparison_id)

    if comparison is None:
        raise NOT_FOUND

    db_session.delete(comparison)
    db_session.commit()

    return {"message": "Comparison deleted"}
