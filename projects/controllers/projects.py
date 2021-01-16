# -*- coding: utf-8 -*-
"""Projects controller."""
from datetime import datetime
from os.path import join

from sqlalchemy import asc, desc, func
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.experiments import ExperimentController
from projects.controllers.utils import list_objects, objects_uuid, uuid_alpha
from projects.models import Experiment, Operator, Project
from projects.object_storage import remove_objects


NOT_FOUND = NotFound("The specified project does not exist")


class ProjectController:
    def __init__(self, session):
        self.session = session
        self.experiment_controller = ExperimentController(session)

    def raise_if_project_does_not_exist(self, project_id):
        """
        Raises an exception if the specified project does not exist.

        Parameters
        ----------
        project_id :str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(Project.uuid) \
            .filter_by(uuid=project_id) \
            .scalar() is not None

        if not exists:
            raise NotFound("The specified project does not exist")

    def list_projects(self, page=1, page_size=10, order_by=None, **filters):
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
        query = self.session.query(Project)
        query_total = self.session.query(func.count(Project.uuid))

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
            "projects": projects,
        }

    def create_project(self, name=None, **kwargs):
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

        check_project_name = self.session.query(Project) \
            .filter_by(name=name) \
            .first()
        if check_project_name:
            raise BadRequest("a project with that name already exists")

        project = Project(uuid=uuid_alpha(), name=name, description=kwargs.get("description"))
        self.session.add(project)
        self.experiment_controller.create_experiment(name="Experimento 1", project_id=project.uuid)
        return project

    def get_project(self, project_id):
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
        project = self.session.query(Project).get(project_id)

        if project is None:
            raise NOT_FOUND

        return project

    def update_project(self, project_id, **kwargs):
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
        project = self.session.query(Project).get(project_id)

        if project is None:
            raise NOT_FOUND

        if "name" in kwargs:
            name = kwargs["name"]
            if name != project.name:
                check_project_name = self.session.query(Project) \
                    .filter_by(name=name) \
                    .first()
                if check_project_name:
                    raise BadRequest("a project with that name already exists")

        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)

        try:
            self.session.query(Project) \
                .filter_by(uuid=project_id) \
                .update(data)
        except (InvalidRequestError, ProgrammingError) as e:
            raise BadRequest(str(e))

        return project

    def delete_project(self, project_id):
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
        project = self.session.query(Project).get(project_id)

        if project is None:
            raise NOT_FOUND

        experiments = self.session.query(Experiment).filter(Experiment.project_id == project_id).all()
        for experiment in experiments:
            # remove operators
            self.session.query(Operator).filter(Operator.experiment_id == experiment.uuid).delete()

        self.session.query(Experiment).filter(Experiment.project_id == project_id).delete()

        self.session.delete(project)

        prefix = join("experiments", project_id)
        remove_objects(prefix=prefix)

        return {"message": "Project deleted"}

    def delete_multiple_projects(self, project_ids):
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

        projects = self.session.query(Project) \
            .filter(Project.uuid.in_(all_projects_ids)) \
            .all()
        experiments = self.session.query(Experiment) \
            .filter(Experiment.project_id.in_(objects_uuid(projects))) \
            .all()
        operators = self.session.query(Operator) \
            .filter(Operator.experiment_id.in_(objects_uuid(experiments))) \
            .all()
        self.pre_delete(projects, total_elements, operators, experiments, all_projects_ids)
        for experiment in experiments:
            prefix = join("experiments", experiment.uuid)
            try:
                remove_objects(prefix=prefix)
            except Exception:
                pass
        return {"message": "Successfully removed projects"}

    def pre_delete(self, projects, total_elements, operators, experiments, all_projects_ids):
        """
        SQL form for deleting multiple projects.

        Parameters
        ----------
        projects : list
        total_elements : int
        operators : list
        experiments : list
        all_projects_ids: str

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
            self.session.execute(operators)
        if len(experiments):
            deleted_experiments = Experiment.__table__.delete().where(Experiment.uuid.in_(objects_uuid(experiments)))
            self.session.execute(deleted_experiments)
        deleted_projects = Project.__table__.delete().where(Project.uuid.in_(all_projects_ids))
        self.session.execute(deleted_projects)
