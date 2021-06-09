# -*- coding: utf-8 -*-
"""Tasks controller."""
import json
import os
import pkgutil
import re
import tempfile
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy import asc, desc

from projects import __version__, models, schemas
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, Forbidden, NotFound
from projects.kubernetes.notebook import copy_file_to_pod, handle_task_creation, \
    update_task_config_map, update_persistent_volume_claim, remove_persistent_volume_claim

PREFIX = "tasks"
VALID_TAGS = ["DATASETS", "DEFAULT", "DESCRIPTIVE_STATISTICS", "FEATURE_ENGINEERING",
              "PREDICTOR", "COMPUTER_VISION", "NLP", "MONITORING"]
DEPLOYMENT_NOTEBOOK = json.loads(pkgutil.get_data("projects", "config/Deployment.ipynb"))
EXPERIMENT_NOTEBOOK = json.loads(pkgutil.get_data("projects", "config/Experiment.ipynb"))

TASK_DEFAULT_EXPERIMENT_IMAGE = os.getenv(
    "TASK_DEFAULT_EXPERIMENT_IMAGE",
    f"platiagro/platiagro-experiment-image:{__version__}",
)
TASK_DEFAULT_CPU_LIMIT = os.getenv("TASK_DEFAULT_CPU_LIMIT", "2000m")
TASK_DEFAULT_CPU_REQUEST = os.getenv("TASK_DEFAULT_CPU_REQUEST", "100m")
TASK_DEFAULT_MEMORY_LIMIT = os.getenv("TASK_DEFAULT_MEMORY_LIMIT", "10Gi")
TASK_DEFAULT_MEMORY_REQUEST = os.getenv("TASK_DEFAULT_MEMORY_REQUEST", "2Gi")
TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS = int(os.getenv(
    "TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS",
    "60",
))

NOT_FOUND = NotFound("The specified task does not exist")


class TaskController:
    def __init__(self, session, background_tasks=None):
        self.session = session
        self.background_tasks = background_tasks

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

        if not isinstance(task.name, str):
            task.name = self.generate_name_task("Tarefa em branco")

        if task.copy_from and has_notebook:
            raise BadRequest("Either provide notebooks or a task to copy from")

        if not task.tags or len(task.tags) == 0:
            task.tags = ["DEFAULT"]

        if any(tag not in VALID_TAGS for tag in task.tags):
            valid_str = ",".join(VALID_TAGS)
            raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

        # check if image is a valid docker image
        self.raise_if_invalid_docker_image(task.image)

        check_comp_name = self.session.query(models.Task).filter_by(name=task.name).first()
        if check_comp_name:
            raise BadRequest("a task with that name already exists")

        # creates a task with specified name,
        # but copies notebooks from a source task
        stored_task_name = None
        if task.copy_from:
            stored_task = self.session.query(models.Task).get(task.copy_from)
            if stored_task is None:
                raise BadRequest("source task does not exist")

            task.image = stored_task.image
            task.commands = stored_task.commands
            task.arguments = stored_task.arguments
            task.parameters = stored_task.parameters
            stored_task_name = stored_task.name
            experiment_notebook_path = stored_task.experiment_notebook_path
            deployment_notebook_path = stored_task.deployment_notebook_path
            task.cpu_limit = stored_task.cpu_limit
            task.cpu_request = stored_task.cpu_request
            task.memory_limit = stored_task.memory_limit
            task.memory_request = stored_task.memory_request
        else:
            # relative path to the mount_path
            experiment_notebook_path = "Experiment.ipynb"
            deployment_notebook_path = "Deployment.ipynb"

        task_id = str(uuid_alpha())

        # loads a sample notebook if none was sent
        if task.experiment_notebook is None:
            task.experiment_notebook = EXPERIMENT_NOTEBOOK

        if task.deployment_notebook is None:
            task.deployment_notebook = DEPLOYMENT_NOTEBOOK

        self.background_tasks.add_task(
            handle_task_creation,
            task=task,
            task_id=task_id,
            experiment_notebook_path=experiment_notebook_path,
            deployment_notebook_path=deployment_notebook_path,
            copy_name=stored_task_name,
        )

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

        if task.tags and any(tag not in VALID_TAGS for tag in task.tags):
            valid_str = ",".join(VALID_TAGS)
            raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

        stored_task = self.session.query(models.Task).get(task_id)

        # If the contents of experiment/deployment notebook were sent,
        # saves them to the notebook server pod
        self.copy_notebooks_to_pod(task, stored_task)

        # checks whether task.name has changed
        if stored_task.name != task.name and task.name:
            # update the volume for the task in the notebook server
            self.background_tasks.add_task(
                update_persistent_volume_claim,
                name=f"vol-task-{task_id}",
                mount_path=f"/home/jovyan/tasks/{task.name}"
            )

        # update ConfigMap for monitoring tasks
        if ((task.parameters and "MONITORING" in stored_task.tags) or
                ("MONITORING" in task.tags if task.tags else False)):
            self.background_tasks.add_task(
                update_task_config_map,
                task_name=stored_task.name,
                task_id=task_id,
                experiment_notebook_path=stored_task.experiment_notebook_path,
            )

        update_data = task.dict(exclude_unset=True)
        update_data.pop("experiment_notebook", None)
        update_data.pop("deployment_notebook", None)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Task).filter_by(uuid=task_id).update(update_data)
        self.session.commit()

        task = self.session.query(models.Task).get(task_id)

        return schemas.Task.from_orm(task)

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

        # remove the volume for the task in the notebook server
        self.background_tasks.add_task(
            remove_persistent_volume_claim,
            name=f"vol-task-{task_id}",
            mount_path=f"/home/jovyan/tasks/{task.name}",
        )

        self.session.delete(task)
        self.session.commit()
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

    def copy_notebooks_to_pod(self, task, stored_task):
        """
        Copies the notebook contents to the pod (if it was sent on TaskUpdate).

        Parameters
        ----------
        task : projects.schemas.task.TaskUpdate
        stored_task : projects.models.task.Task
        """
        if task.experiment_notebook:
            with tempfile.NamedTemporaryFile("w", delete=False) as f:
                json.dump(task.experiment_notebook, f)

            task.experiment_notebook_path = stored_task.experiment_notebook_path

            if task.experiment_notebook_path is None:
                task.experiment_notebook_path = "Experiment.ipynb"

            filepath = f.name
            destination_path = f"{stored_task.name}/{task.experiment_notebook_path}"
            copy_file_to_pod(filepath, destination_path)
            os.remove(filepath)

        if task.deployment_notebook:
            with tempfile.NamedTemporaryFile("w", delete=False) as f:
                json.dump(task.deployment_notebook, f)

            task.deployment_notebook_path = stored_task.deployment_notebook_path

            if task.deployment_notebook_path is None:
                task.deployment_notebook_path = "Deployment.ipynb"

            filepath = f.name
            destination_path = f"{stored_task.name}/{task.deployment_notebook_path}"
            copy_file_to_pod(filepath, destination_path)
            os.remove(filepath)
