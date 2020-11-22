# -*- coding: utf-8 -*-
"""Projects controller."""
from datetime import datetime
from os.path import join

from sqlalchemy import asc, desc, func
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.experiments import create_experiment
from projects.controllers.utils import list_objects, objects_uuid, uuid_alpha
from projects.database import db_session
from projects.models import Experiment, Operator, Project
from projects.object_storage import remove_objects


NOT_FOUND = NotFound("The specified project does not exist")


def list_projects(page=1, page_size=10, order_by=None, **filters):
    """
    Lists projects. Supports pagination, and sorting.

    Parameters
    ----------
    page : int
        The page number. First page is 1.
    page_size : int
        The page size. Default value is 10.
    order_by : str
        Order by instruction. Format is "column [asc|desc]".
    **filters : dict

    Returns
    -------
    dict
        One page of projects and the total of records.

    Raises
    ------
    BadRequest
        When order_by is invalid.
    """
    query = db_session.query(Project)
    query_total = db_session.query(func.count(Project.uuid))

    # Apply filters to the query
    for column, value in filters.items():
        query = query.filter(getattr(Project, column).ilike(f"%{value}%"))
        query_total = query_total.filter(getattr(Project, column).ilike(f"%{value}%"))

    total = query_total.scalar()

    # Default sort is name in ascending order
    if not order_by:
        order_by = "name asc"

    # Sorts records
    try:
        (column, sort) = order_by.split()
        assert sort.lower() in ["asc", "desc"]
        assert column in Project.__table__.columns.keys()
    except (AssertionError, ValueError):
        raise BadRequest("Invalid order argument")

    if sort.lower() == "asc":
        query = query.order_by(asc(getattr(Project, column)))
    elif sort.lower() == "desc":
        query = query.order_by(desc(getattr(Project, column)))

    # Applies pagination
    query = query.limit(page_size).offset((page - 1) * page_size)
    projects = query.all()

    return {
        "total": total,
        "projects": [project.as_dict() for project in projects]
    }


def create_project(name=None, **kwargs):
    """
    Creates a new project in our database.

    Parameters
    ----------
    name : str
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The project attributes.

    Raises
    ------
    BadRequest
        When the `**kwargs` (project attributes) are invalid.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    check_project_name = db_session.query(Project) \
        .filter_by(name=name) \
        .first()
    if check_project_name:
        raise BadRequest("a project with that name already exists")

    project = Project(uuid=uuid_alpha(), name=name, description=kwargs.get("description"))
    db_session.add(project)
    db_session.commit()
    create_experiment(name="Experimento 1", project_id=project.uuid)
    return project.as_dict()


def get_project(project_id):
    """
    Details a project from our database.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    dict
        The project attributes.

    Raises
    ------
    NotFound
        When project_id does not exist.
    """
    project = Project.query.get(project_id)

    if project is None:
        raise NOT_FOUND

    return project.as_dict()


def update_project(project_id, **kwargs):
    """
    Updates a project in our database.

    Parameters
    ----------
    project_id str
    **kwargs:
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The project attributes.

    Raises
    ------
    NotFound
        When project_id does not exist.
    BadRequest
        When the `**kwargs` (project attributes) are invalid.
    """
    project = Project.query.get(project_id)

    if project is None:
        raise NOT_FOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != project.name:
            check_project_name = db_session.query(Project) \
                .filter_by(name=name) \
                .first()
            if check_project_name:
                raise BadRequest("a project with that name already exists")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Project) \
            .filter_by(uuid=project_id) \
            .update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return project.as_dict()


def delete_project(project_id):
    """
    Delete a project in our database and in the object storage.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    dict
        The deletion result.

    Raises
    ------
    NotFound
        When project_id does not exist.
    """
    project = Project.query.get(project_id)

    if project is None:
        raise NOT_FOUND

    experiments = Experiment.query.filter(Experiment.project_id == project_id).all()
    for experiment in experiments:
        # remove operators
        Operator.query.filter(Operator.experiment_id == experiment.uuid).delete()

    Experiment.query.filter(Experiment.project_id == project_id).delete()

    db_session.delete(project)
    db_session.commit()

    prefix = join("experiments", project_id)
    remove_objects(prefix=prefix)

    return {"message": "Project deleted"}


def delete_multiple_projects(project_ids):
    """
    Delete multiple projects.

    Parameters
    ----------
    project_ids : str
        The list of project ids.

    Returns
    -------
    dict
        The deletion result.

    Raises
    ------
    BadRequest
        When any project_id does not exist.
    """
    total_elements = len(project_ids)
    all_projects_ids = list_objects(project_ids)
    if total_elements < 1:
        raise BadRequest("inform at least one project")

    projects = db_session.query(Project) \
        .filter(Project.uuid.in_(all_projects_ids)) \
        .all()
    experiments = db_session.query(Experiment) \
        .filter(Experiment.project_id.in_(objects_uuid(projects))) \
        .all()
    operators = db_session.query(Operator) \
        .filter(Operator.experiment_id.in_(objects_uuid(experiments))) \
        .all()
    session = pre_delete(db_session, projects, total_elements, operators, experiments, all_projects_ids)
    for experiment in experiments:
        prefix = join("experiments", experiment.uuid)
        try:
            remove_objects(prefix=prefix)
        except Exception:
            pass
    session.commit()
    return {"message": "Successfully removed projects"}


def pre_delete(db_session, projects, total_elements, operators, experiments, all_projects_ids):
    """
    SQL form for deleting multiple projects.

    Parameters
    ----------
    db_session : db_session
    projects : list
    total_elements : int
    operators : list
    experiments : list
    all_projects_ids: str

    Returns
    -------
    sqlalchemy.orm.session.Session

    Raises
    ------
    NotFound
        When any project_id does not exist.
    """
    if len(projects) != total_elements:
        raise NOT_FOUND
    if len(operators):
        # remove operators
        operators = Operator.__table__.delete().where(Operator.experiment_id.in_(objects_uuid(experiments)))
        db_session.execute(operators)
    if len(experiments):
        deleted_experiments = Experiment.__table__.delete().where(Experiment.uuid.in_(objects_uuid(experiments)))
        db_session.execute(deleted_experiments)
    deleted_projects = Project.__table__.delete().where(Project.uuid.in_(all_projects_ids))
    db_session.execute(deleted_projects)
    return db_session
