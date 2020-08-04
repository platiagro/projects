# -*- coding: utf-8 -*-
"""Projects controller."""
import re
from datetime import datetime
from os.path import join

from sqlalchemy import func
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from .experiments import create_experiment
from ..database import db_session
from ..models import Dependency, Experiment, Operator, Project
from ..object_storage import remove_objects
from .utils import uuid_alpha, list_objects, objects_uuid


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
    create_experiment(name="Novo experimento", project_id=project.uuid)
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
        raise NotFound("The specified project does not exist")

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


def pagination_projects(name, page, page_size):
    """The numbers of items to return maximum 100 """
    if page_size > 100:
        page_size = 100
    query = db_session.query(Project)
    if name:
        query = query.filter(Project.name.ilike(func.lower(f"%{name}%")))
    if page != 0:
        query = query.order_by(Project.name).limit(page_size).offset((page - 1) * page_size)
    projects = query.all()
    projects.sort(key=lambda o: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", o.name)])
    return [project.as_dict() for project in projects]


def total_rows_projects(name):
    query = db_session.query(func.count(Project.uuid))
    if name:
        query = query.filter(Project.name.ilike(func.lower(f"%{name}%")))
    rows = query.scalar()
    return rows


def delete_projects(project_ids):
    total_elements = len(project_ids)
    all_projects_ids = list_objects(project_ids)
    if total_elements < 1:
        return {"message": "please inform the uuid of the project"}
    projects = db_session.query(Project).filter(Project.uuid.in_(all_projects_ids)).all()
    experiments = db_session.query(Experiment).filter(Experiment.project_id.in_(objects_uuid(projects))).all()
    operators = db_session.query(Operator).filter(Operator.experiment_id.in_(objects_uuid(experiments))) \
        .all()
    if len(projects) != total_elements:
        raise NotFound("The specified project does not exist")
    if len(operators) != 0:
        # remove dependencies
        for operator in operators:
            Dependency.query.filter(Dependency.operator_id == operator.uuid).delete()
        # remove operators
        operators = Operator.__table__.delete().where(Operator.experiment_id.in_(objects_uuid(experiments)))
        db_session.execute(operators)
    if len(experiments) != 0:
        deleted_experiments = Experiment.__table__.delete().where(Experiment.uuid.in_(objects_uuid(experiments)))
        db_session.execute(deleted_experiments)
    deleted_projects = Project.__table__.delete().where(Project.uuid.in_(all_projects_ids))
    db_session.execute(deleted_projects)
    for experiment in experiments:
        prefix = join("experiments", experiment.uuid)
        try:
            remove_objects(prefix=prefix)
        except Exception:
            pass
    db_session.commit()

    return {"message": "Successfully removed projects"}
