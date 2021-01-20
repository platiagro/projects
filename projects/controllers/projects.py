# -*- coding: utf-8 -*-
"""Projects controller."""
from datetime import datetime
from os.path import join
from typing import Optional

from sqlalchemy import asc, desc, func

from projects import models, schemas
from projects.controllers.experiments import ExperimentController
from projects.controllers.utils import list_objects, objects_uuid, uuid_alpha
from projects.exceptions import BadRequest, NotFound
from projects.object_storage import remove_objects

NOT_FOUND = NotFound("The specified project does not exist")


class ProjectController:
    def __init__(self, session):
        self.session = session
        self.experiment_controller = ExperimentController(session)

    def raise_if_project_does_not_exist(self, project_id: str):
        """
        Raises an exception if the specified project does not exist.

        Parameters
        ----------
        project_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Project.uuid) \
            .filter_by(uuid=project_id) \
            .scalar() is not None

        if not exists:
            raise NOT_FOUND

    def list_projects(self, page: Optional[int] = 1, page_size: Optional[int] = 10, order_by: Optional[str] = None):
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

        Returns
        -------
        projects.schemas.project.ProjectList

        Raises
        ------
        BadRequest
            When order_by is invalid.
        """
        query = self.session.query(models.Project)
        query_total = self.session.query(func.count(models.Project.uuid))

        # FIXME Apply filters to the query
        # for column, value in filters.items():
        #     query = query.filter(getattr(models.Project, column).ilike(f"%{value}%"))
        #     query_total = query_total.filter(getattr(models.Project, column).ilike(f"%{value}%"))

        total = query_total.scalar()

        # Default sort is name in ascending order
        if not order_by:
            order_by = "name asc"

        # Sorts records
        try:
            (column, sort) = order_by.split()
            assert sort.lower() in ["asc", "desc"]
            assert column in models.Project.__table__.columns.keys()
        except (AssertionError, ValueError):
            raise BadRequest("Invalid order argument")

        if sort.lower() == "asc":
            query = query.order_by(asc(getattr(models.Project, column)))
        elif sort.lower() == "desc":
            query = query.order_by(desc(getattr(models.Project, column)))

        # Applies pagination
        query = query.limit(page_size).offset((page - 1) * page_size)
        projects = query.all()

        return schemas.ProjectList.from_model(projects, total)

    def create_project(self, project: schemas.ProjectCreate):
        """
        Creates a new project in our database.

        Parameters
        ----------
        project: projects.schemas.project.ProjectCreate

        Returns
        -------
        project: projects.schemas.project.Project

        Raises
        ------
        BadRequest
            When the project attributes are invalid.
        """
        if not isinstance(project.name, str):
            raise BadRequest("name is required")

        store_project = self.session.query(models.Project) \
            .filter_by(name=project.name) \
            .first()
        if store_project:
            raise BadRequest("a project with that name already exists")

        project = models.Project(uuid=uuid_alpha(), name=project.name, description=project.description)
        self.session.add(project)
        self.session.flush()

        experiment = schemas.ExperimentCreate(name="Experimento 1")
        self.experiment_controller.create_experiment(experiment=experiment, project_id=project.uuid)

        self.session.commit()
        self.session.refresh(project)

        return schemas.Project.from_model(project)

    def get_project(self, project_id: str):
        """
        Details a project from our database.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        projects.schemas.project.Project

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        project = self.session.query(models.Project).get(project_id)

        if project is None:
            raise NOT_FOUND

        return schemas.Project.from_model(project)

    def update_project(self, project: schemas.ProjectUpdate, project_id: str):
        """
        Updates a project in our database.

        Parameters
        ----------
        project: projects.schemas.project.ProjectUpdate
        project_id: str

        Returns
        -------
        project: projects.schemas.project.Project

        Raises
        ------
        NotFound
            When project_id does not exist.
        BadRequest
            When the project attributes are invalid.
        """
        self.raise_if_project_does_not_exist(project_id)

        stored_project = self.session.query(models.Project) \
            .filter_by(name=project.name) \
            .first()
        if stored_project and stored_project.uuid != project_id:
            raise BadRequest("a project with that name already exists")

        update_data = project.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Project).filter_by(uuid=project_id).update(update_data)
        self.session.commit()

        project = self.session.query(models.Project).get(project_id)

        return schemas.Project.from_model(project)

    def delete_project(self, project_id):
        """
        Delete a project in our database and in the object storage.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        project = self.session.query(models.Project).get(project_id)

        if project is None:
            raise NOT_FOUND

        deployments = self.session.query(models.Deployment).filter(models.Deployment.project_id == project_id).all()
        for deployment in deployments:
            self.session.query(models.Operator).filter(models.Operator.deployment_id == deployment.uuid).delete()
        self.session.query(models.Deployment).filter(models.Deployment.project_id == project_id).delete()

        experiments = self.session.query(models.Experiment).filter(models.Experiment.project_id == project_id).all()
        for experiment in experiments:
            self.session.query(models.Operator).filter(models.Operator.experiment_id == experiment.uuid).delete()
        self.session.query(models.Experiment).filter(models.Experiment.project_id == project_id).delete()

        self.session.delete(project)

        prefix = join("experiments", project_id)
        remove_objects(prefix=prefix)

        return schemas.Message(message="Project deleted")

    def delete_multiple_projects(self, project_ids):
        """
        Delete multiple projects.

        Parameters
        ----------
        project_ids : str
            The list of project ids.

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        BadRequest
            When any project_id does not exist.
        """
        total_elements = len(project_ids)
        all_projects_ids = list_objects(project_ids)
        if total_elements < 1:
            raise BadRequest("inform at least one project")

        projects = self.session.query(models.Project) \
            .filter(models.Project.uuid.in_(all_projects_ids)) \
            .all()
        experiments = self.session.query(models.Experiment) \
            .filter(models.Experiment.project_id.in_(objects_uuid(projects))) \
            .all()
        operators = self.session.query(models.Operator) \
            .filter(models.Operator.experiment_id.in_(objects_uuid(experiments))) \
            .all()
        self.pre_delete(projects, total_elements, operators, experiments, all_projects_ids)
        for experiment in experiments:
            prefix = join("experiments", experiment.uuid)
            try:
                remove_objects(prefix=prefix)
            except Exception:
                pass

        return schemas.Message(message="Successfully removed projects")

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
            operators = models.Operator.__table__.delete().where(models.Operator.experiment_id.in_(objects_uuid(experiments)))
            self.session.execute(operators)
        if len(experiments):
            deleted_experiments = models.Experiment.__table__.delete().where(models.Experiment.uuid.in_(objects_uuid(experiments)))
            self.session.execute(deleted_experiments)
        deleted_projects = models.Project.__table__.delete().where(models.Project.uuid.in_(all_projects_ids))
        self.session.execute(deleted_projects)
