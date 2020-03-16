# -*- coding: utf-8 -*-
"""Projects controller."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Project


def list_projects():
    """Lists all projects from our database.

    Returns:
        A list of all projects ids.
    """
    projects = Project.query.all()
    return [project.as_dict() for project in projects]


def create_project(name=None, **kwargs):
    """Creates a new project in our database.

    Args:
        name (str): the project name.

    Returns:
        The project info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    project = Project(uuid=str(uuid4()), name=name)
    db_session.add(project)
    db_session.commit()
    return project.as_dict()


def get_project(uuid):
    """Details a project from our database.

    Args:
        uuid (str): the project uuid to look for in our database.

    Returns:
        The project info.
    """
    project = Project.query.get(uuid)

    if project is None:
        raise NotFound("The specified project does not exist")

    return project.as_dict()


def update_project(uuid, **kwargs):
    """Updates a project in our database.

    Args:
        uuid (str): the project uuid to look for in our database.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The project info.
    """
    project = Project.query.get(uuid)

    if project is None:
        raise NotFound("The specified project does not exist")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Project).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return project.as_dict()
