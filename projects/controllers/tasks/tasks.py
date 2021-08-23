# -*- coding: utf-8 -*-
"""Tasks controller."""
import json
import pkgutil
import re
from datetime import datetime
from typing import Optional

from sqlalchemy import asc, desc, func

from projects import kfp, models, schemas
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, Forbidden, NotFound

PREFIX = "tasks"
VALID_CATEGORIES = ["DATASETS", "DEFAULT", "DESCRIPTIVE_STATISTICS", "FEATURE_ENGINEERING",
                    "PREDICTOR", "COMPUTER_VISION", "NLP", "MONITORING"]
DEPLOYMENT_NOTEBOOK = json.loads(pkgutil.get_data("projects", "config/Deployment.ipynb").decode())
EXPERIMENT_NOTEBOOK = json.loads(pkgutil.get_data("projects", "config/Experiment.ipynb").decode())

NOT_FOUND = NotFound("The specified task does not exist")


class TaskController:
    def __init__(self, session):
        self.session = session

    def raise_if_task_does_not_exist(self, task_id: str):
        """
        Raises an exception if the specified task does not exist.

        Parameters
        ----------
        task_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Task.uuid) \
            .filter_by(uuid=task_id) \
            .scalar() is not None

        if not exists:
            raise NOT_FOUND

    def list_tasks(self,
                   page: Optional[int] = None,
                   page_size: Optional[int] = None,
                   order_by: str = Optional[str],
                   **filters):
        """
        Lists tasks. Supports pagination, and sorting.

        Parameters
        ----------
        page : int
            The page number. First page is 1.
        page_size : int
            The page size.
        order_by : str
            Order by instruction. Format is "column [asc|desc]".
        **filters : dict

        Returns
        -------
        projects.schemas.task.TaskList

        Raises
        ------
        BadRequest
            When order_by is invalid.
        """
        query = self.session.query(models.Task)
        query_total = self.session.query(func.count(models.Task.uuid))

        for column, value in filters.items():
            query = query.filter(getattr(models.Task, column).ilike(f"%{value}%"))
            query_total = query_total.filter(getattr(models.Task, column).ilike(f"%{value}%"))

        total = query_total.scalar()

        # Default sort is name in ascending order
        if not order_by:
            order_by = "name asc"

        # Sorts records
        try:
            (column, sort) = order_by.replace('+', ' ').strip().split()
            assert sort.lower() in ["asc", "desc"]
            assert column in models.Task.__table__.columns.keys()
        except (AssertionError, ValueError):
            raise BadRequest("Invalid order argument")

        if sort.lower() == "asc":
            query = query.order_by(asc(getattr(models.Task, column)))
        elif sort.lower() == "desc":
            query = query.order_by(desc(getattr(models.Task, column)))

        if page and page_size:
            # Applies pagination
            query = query.limit(page_size).offset((page - 1) * page_size)

        tasks = query.all()
        return schemas.TaskList.from_orm(tasks, total)

    def generate_name_task(self, name, attempt=1):
        name_task = f"{name} - {attempt}"
        check_comp_name = self.session.query(models.Task).filter_by(name=name_task).first()
        if check_comp_name:
            return self.generate_name_task(name, attempt + 1)
        return name_task
      
    def task_category_is_not_none(self, task_cat):
        if task_cat.category is not None and task_cat.category not in VALID_CATEGORIES:
            valid_str = ",".join(VALID_CATEGORIES)
            raise BadRequest(f"Invalid category. Choose any of {valid_str}")

    def create_task(self, task: schemas.TaskCreate):
        """
        Creates a new task in our database and a volume claim in the cluster.

        Parameters
        ----------
        task: projects.schemas.task.TaskCreate

        Returns
        -------
        projects.schemas.task.Task

        Raises
        ------
        BadRequest
            When task attributes are invalid.
        """
        has_notebook = task.experiment_notebook or task.deployment_notebook

        if task.copy_from and has_notebook:
            raise BadRequest("Either provide notebooks or a task to copy from")

        if not task.tags:
            task.tags = ["DEFAULT"]
        
        self.task_category_is_not_none(task)

        # check if image is a valid docker image
        self.raise_if_invalid_docker_image(task.image)

        check_comp_name = self.session.query(models.Task).filter_by(name=task.name).first()
        if check_comp_name:
            raise BadRequest("a task with that name already exists")

        # creates a task with specified name,
        # but copies notebooks from a source task
        stored_task = None
        if task.copy_from:
            stored_task = self.session.query(models.Task).get(task.copy_from)
            if stored_task is None:
                raise BadRequest("source task does not exist")

            task.image = stored_task.image
            task.commands = stored_task.commands
            task.arguments = stored_task.arguments
            task.parameters = stored_task.parameters
            experiment_notebook_path = stored_task.experiment_notebook_path
            deployment_notebook_path = stored_task.deployment_notebook_path
            task.cpu_limit = stored_task.cpu_limit
            task.cpu_request = stored_task.cpu_request
            task.memory_limit = stored_task.memory_limit
            task.memory_request = stored_task.memory_request
            # Adding the task name if it is a copy.
            task.name = self.generate_name_task(f"{stored_task.name} - Cópia")

        else:
            if not isinstance(task.name, str):
                task.name = self.generate_name_task("Tarefa em branco")
            if task.image is not None:
                experiment_notebook_path = None
                deployment_notebook_path = None
                task.experiment_notebook = None
                task.deployment_notebook = None
            else:
                # relative path to the mount_path
                experiment_notebook_path = "Experiment.ipynb"
                deployment_notebook_path = "Deployment.ipynb"
                task.experiment_notebook = EXPERIMENT_NOTEBOOK
                task.deployment_notebook = DEPLOYMENT_NOTEBOOK

        task_id = str(uuid_alpha())

        task_dict = task.dict(exclude_unset=True)
        task_dict.pop("copy_from", None)
        task_dict.pop("experiment_notebook", None)
        task_dict.pop("deployment_notebook", None)
        task_dict["uuid"] = task_id
        task_dict["experiment_notebook_path"] = experiment_notebook_path
        task_dict["deployment_notebook_path"] = deployment_notebook_path

        # saves task info to the database
        task = models.Task(**task_dict)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        all_tasks = self.session.query(models.Task).all()

        kfp.create_task(
            task=task,
            namespace=kfp.KF_PIPELINES_NAMESPACE,
            all_tasks=all_tasks,
            copy_from=stored_task,
        )

        return schemas.Task.from_orm(task)

    def get_task(self, task_id):
        """
        Details a task from our database.

        Parameters
        ----------
        task_id : str

        Returns
        -------
        projects.schemas.task.Task

        Raises
        ------
        NotFound
            When task_id does not exist.
        """
        task = self.session.query(models.Task).get(task_id)

        if task is None:
            raise NOT_FOUND

        return schemas.Task.from_orm(task)

    def update_task(self, task: schemas.TaskUpdate, task_id: str):
        """
        Updates a task in our database/object storage.

        Parameters
        ----------
        task: projects.schemas.task.TaskUpdate
        task_id : str

        Returns
        -------
        task: projects.schemas.task.Task

        Raises
        ------
        NotFound
            When task_id does not exist.
        BadRequest
            When task attributes are invalid.
        """
        self.raise_if_task_does_not_exist(task_id)

        stored_task = self.session.query(models.Task) \
            .filter_by(name=task.name) \
            .first()
        if stored_task and stored_task.uuid != task_id:
            raise BadRequest("a task with that name already exists")

        if task.category is not None and task.category not in VALID_CATEGORIES:
            valid_str = ",".join(VALID_CATEGORIES)
            raise BadRequest(f"Invalid category. Choose any of {valid_str}")

        stored_task = self.session.query(models.Task).get(task_id)

        # checks whether any changes that start a pipeline occured.
        # when the name of a task has changed, JupyterLab must reflect this change.
        name_has_changed = stored_task.name != task.name and task.name
        # if the contents of a notebook are sent, the files on JupyterLab must be updated
        experiment_notebook = task.experiment_notebook
        deployment_notebook = task.deployment_notebook
        notebooks_have_changed = experiment_notebook or deployment_notebook

        update_data = task.dict(exclude_unset=True)
        update_data.pop("experiment_notebook", None)
        update_data.pop("deployment_notebook", None)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Task) \
            .filter_by(uuid=task_id) \
            .update(update_data)
        self.session.commit()

        task = self.session.query(models.Task).get(task_id)

        if name_has_changed or notebooks_have_changed:
            all_tasks = self.session.query(models.Task).all()

            kfp.update_task(
                task=task,
                all_tasks=all_tasks,
                namespace=kfp.KF_PIPELINES_NAMESPACE,
                experiment_notebook=experiment_notebook,
                deployment_notebook=deployment_notebook,
            )

        return schemas.Task.from_orm(task)

    def get_or_create_dataset_task_if_not_exist(self):
        """
        Get or create a dataset  task if the operator has none.

        Returns
        -------
        dataset_task.uuid: str
        """

        dataset_task = self.session.query(models.Task).filter_by(category="DATASETS").first()
        if dataset_task is None:
            dataset_task_schema = schemas.TaskCreate(
                name="Upload de arquivo",
                description="Importa arquivos para utilização em experimentos.",
                category="DATASETS",
                tags=["DATASETS"],
                commands=None,
                arguments=None,
                image=models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
                cpu_limit=models.task.TASK_DEFAULT_CPU_LIMIT,
                cpu_request=models.task.TASK_DEFAULT_CPU_REQUEST,
                memory_limit=models.task.TASK_DEFAULT_MEMORY_LIMIT,
                memory_request=models.task.TASK_DEFAULT_MEMORY_REQUEST,
            )

            # BUG
            # This call performs a session.commit(), but current transaction
            # is not over yet. We should refactor this code.
            dataset_task = self.create_task(task=dataset_task_schema)
        return dataset_task.uuid

    def delete_task(self, task_id: str):
        """
        Delete a task in our database.

        Parameters
        ----------
        task_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When task_id does not exist.
        """
        task = self.session.query(models.Task).get(task_id)

        if task is None:
            raise NOT_FOUND

        if task.operator:
            raise Forbidden("Task related to an operator")

        self.session.delete(task)
        self.session.commit()

        # remove the volume for the task in the notebook server
        all_tasks = self.session.query(models.Task).all()
        kfp.delete_task(
            task=task,
            all_tasks=all_tasks,
            namespace=kfp.KF_PIPELINES_NAMESPACE,
        )

        return schemas.Message(message="Task deleted")

    def raise_if_invalid_docker_image(self, image):
        """
        Raise an error if a str does not meet the standards for a docker image name.

        Example: (username/organization)/name-of-the-image:tag

        Parameters
        ----------
        image : str or None
            The image name.

        Raises
        ------
        BadRequest
            When a given image is a invalid one.
        """
        pattern = re.compile("[a-z0-9.-]+([/]{1}[a-z0-9.-]+)+([:]{1}[a-z0-9.-]+){0,1}$")

        if image and pattern.match(image) is None:
            raise BadRequest("invalid docker image name")

    def send_emails(self, email_schema, task_id):
        """
        Handles mailing of contents of task

        Parameters
        ----------
        task_id : str

        Returns
        -------
        message: str
        """

        task = self.session.query(models.Task).get(task_id)
        if task is None:
            raise NOT_FOUND

        kfp.send_email(task=task, namespace=kfp.KF_PIPELINES_NAMESPACE)

        return {"message": "email has been sent"}
