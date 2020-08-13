# -*- coding: utf-8 -*-
"""Projects controller."""
import re
from datetime import datetime
from os.path import join

from sqlalchemy import func
from sqlalchemy import asc, desc, text

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from .experiments import create_experiment
from ..database import db_session
from ..models import Dependency, Experiment, Operator, Project
from ..object_storage import remove_objects
from .utils import uuid_alpha, list_objects, objects_uuid, text_to_list


NOT_FOUND = NotFound('The specified project does not exist')


def list_projects():
    """Lists all projects from our database.

    Returns:
        A list of all projects sorted by name in natural sort order.
    """

    projects = db_session.query(Project).all()
    # sort the list in place, using natural sort
    projects.sort(key=lambda o: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", o.name)])
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

    check_project_name = db_session.query(Project).filter_by(name=name).first()
    if check_project_name:
        raise BadRequest("a project with that name already exists")

    project = Project(uuid=uuid_alpha(), name=name, description=kwargs.get("description"))
    db_session.add(project)
    db_session.commit()
    create_experiment(name="Experimento 1", project_id=project.uuid)
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
        raise NOT_FOUND

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
        raise NOT_FOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != project.name:
            check_project_name = db_session.query(Project).filter_by(name=name).first()
            if check_project_name:
                raise BadRequest("a project with that name already exists")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Project).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return project.as_dict()


def delete_project(uuid):
    """Delete a project in our database and in the object storage.

    Args:
        uuid (str): the project uuid to look for in our database.

    Returns:
        The deletion result.
    """
    project = Project.query.get(uuid)

    if project is None:
        raise NOT_FOUND

    experiments = Experiment.query.filter(Experiment.project_id == uuid).all()
    for experiment in experiments:
        # remove dependencies
        operators = db_session.query(Operator).filter(Operator.experiment_id == experiment.uuid).all()
        for operator in operators:
            Dependency.query.filter(Dependency.operator_id == operator.uuid).delete()

        # remove operators
        Operator.query.filter(Operator.experiment_id == experiment.uuid).delete()

    Experiment.query.filter(Experiment.project_id == uuid).delete()

    db_session.delete(project)
    db_session.commit()

    prefix = join("experiments", uuid)
    remove_objects(prefix=prefix)

    return {"message": "Project deleted"}


def pagination_projects(name, page, page_size, order):
    """Pagination ordering

        Args:
            name (str): name of the project to be searched
            page (int): page number
            page_size(int) : record numbers
            order(str): order by Ex: uuid asc

        Returns:
            A list of projects.
        """
    query = db_session.query(Project)
    if name:
        query = query.filter(Project.name.ilike(func.lower(f"%{name}%")))
    if page == 0 and order is None:
        query = query.order_by(text('projects.name'))
    elif page and order is None:
        query = query.order_by(text('name')).limit(page_size).offset((page - 1) * page_size)
    else:
        query = pagination_ordering(query, page_size, page, order)
    projects = query.all()
    return [project.as_dict() for project in projects]


def total_rows_projects(name):
    """Returns the total number of records
    Args:
        name (str):name to be searched

    Returns:
        total records.
    """
    query = db_session.query(func.count(Project.uuid))
    if name:
        query = query.filter(Project.name.ilike(func.lower(f"%{name}%")))
    rows = query.scalar()
    return rows


def delete_multiple_projects(project_ids):
    """ Delete multiple projects
     project_ids (str): list of projects
    """
    total_elements = len(project_ids)
    all_projects_ids = list_objects(project_ids)
    if total_elements < 1:
        return {"message": "please inform the uuid of the project"}
    projects = db_session.query(Project).filter(Project.uuid.in_(all_projects_ids)).all()
    experiments = db_session.query(Experiment).filter(Experiment.project_id.in_(objects_uuid(projects))).all()
    operators = db_session.query(Operator).filter(Operator.experiment_id.in_(objects_uuid(experiments))) \
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
    if len(projects) != total_elements:
        raise NOT_FOUND
    if len(operators):
        # remove dependencies
        for operator in operators:
            Dependency.query.filter(Dependency.operator_id == operator.uuid).delete()
        # remove operators
        operators = Operator.__table__.delete().where(Operator.experiment_id.in_(objects_uuid(experiments)))
        db_session.execute(operators)
    if len(experiments):
        deleted_experiments = Experiment.__table__.delete().where(Experiment.uuid.in_(objects_uuid(experiments)))
        db_session.execute(deleted_experiments)
    deleted_projects = Project.__table__.delete().where(Project.uuid.in_(all_projects_ids))
    db_session.execute(deleted_projects)
    return db_session


def pagination_ordering(query, page_size, page, order_by):
    """Pagination ordering

    Args:
        query (str): query
        page_size(int) : record numbers
        page (int): page number
        order_by (str): order by Ex: uuid asc

    Returns:
        A list of projects.
    """
    if order_by:
        order = text_to_list(order_by)
        if page:
            if order[1]:
                if 'desc' == order[1].lower():
                    query.order_by(desc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
                if 'asc' == order[1].lower():
                    query.order_by(asc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
        else:
            query = uninformed_page(query, order)
    return query


def uninformed_page(query, order):
    """If the page number was not informed just sort by the column name entered
            query (str): query
            order_by (str): order by Ex: uuid asc
        """
    if order[1]:
        if 'asc' == order[1].lower():
            query.order_by(asc(text(f'projects.{order[0]}')))
        if 'desc' == order[1].lower():
            query.order_by(desc(text(f'projects.{order[0]}')))
    return query
