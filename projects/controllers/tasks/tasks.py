# -*- coding: utf-8 -*-
"""Tasks controller."""
import re
from datetime import datetime
from json import dumps, loads
from os.path import join
from pkgutil import get_data

from minio.error import ResponseError
from sqlalchemy import func
from sqlalchemy import asc, desc
from sqlalchemy.exc import InvalidRequestError, IntegrityError, ProgrammingError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from projects.controllers.utils import uuid_alpha
from projects.database import db_session
from projects.jupyter import create_new_file, list_files, delete_file, update_folder_name
from projects.models import Task
from projects.object_storage import BUCKET_NAME, get_object, put_object, \
    list_objects, remove_object

PREFIX = "tasks"
VALID_TAGS = ["DATASETS", "DEFAULT", "DESCRIPTIVE_STATISTICS", "FEATURE_ENGINEERING",
              "PREDICTOR", "COMPUTER_VISION", "NLP"]
DEPLOYMENT_NOTEBOOK = loads(get_data("projects", "config/Deployment.ipynb"))
EXPERIMENT_NOTEBOOK = loads(get_data("projects", "config/Experiment.ipynb"))

NOT_FOUND = NotFound("The specified task does not exist")


def list_tasks(page, page_size, order_by=None, **filters):
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
    dict
        One page of tasks and the total of records.

    Raises
    ------
    BadRequest
        When order_by is invalid.
    """
    query = db_session.query(Task)
    query_total = db_session.query(func.count(Task.uuid))

    # Apply filters to the query
    for column, value in filters.items():
        query = query.filter(getattr(Task, column).ilike(f"%{value}%"))
        query_total = query_total.filter(getattr(Task, column).ilike(f"%{value}%"))

    total = query_total.scalar()

    # Default sort is name in ascending order
    if not order_by:
        order_by = "name asc"

    # Sorts records
    try:
        (column, sort) = order_by.split()
        assert sort.lower() in ["asc", "desc"]
        assert column in Task.__table__.columns.keys()
    except (AssertionError, ValueError):
        raise BadRequest("Invalid order argument")

    if sort.lower() == "asc":
        query = query.order_by(asc(getattr(Task, column)))
    elif sort.lower() == "desc":
        query = query.order_by(desc(getattr(Task, column)))

    if page and page_size:
        # Applies pagination
        query = query.limit(page_size).offset((int(page) - 1) * int(page_size))
    
    tasks = query.all()

    return {
        "total": total,
        "tasks": [task.as_dict() for task in tasks]
    }


def create_task(**kwargs):
    """
    Creates a new task in our database/object storage.

    Parameters
    ----------
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The task attributes.

    Raises
    ------
    BadRequest
        When the `**kwargs` (task attributes) are invalid.
    """
    name = kwargs.get("name", None)
    description = kwargs.get("description", None)
    tags = kwargs.get("tags", ["DEFAULT"])
    image = kwargs.get("image", None)
    commands = kwargs.get("commands", None)
    arguments = kwargs.get("arguments", None)
    experiment_notebook = kwargs.get("experiment_notebook", None)
    deployment_notebook = kwargs.get("deployment_notebook", None)
    is_default = kwargs.get("is_default", None)
    copy_from = kwargs.get("copy_from", None)

    if not isinstance(name, str):
        raise BadRequest("name is required")

    has_notebook = experiment_notebook or deployment_notebook

    if copy_from and has_notebook:
        raise BadRequest("Either provide notebooks or a task to copy from")

    if len(tags) == 0:
        tags = ["DEFAULT"]

    if any(tag not in VALID_TAGS for tag in tags):
        valid_str = ",".join(VALID_TAGS)
        raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

    # check if image is a valid docker image
    raise_if_invalid_docker_image(image)

    check_comp_name = db_session.query(Task).filter_by(name=name).first()
    if check_comp_name:
        raise BadRequest("a task with that name already exists")

    # creates a task with specified name,
    # but copies notebooks from a source task
    if copy_from:
        return copy_task(name, description, tags, copy_from)

    task_id = str(uuid_alpha())

    # loads a sample notebook if none was sent
    if experiment_notebook is None and "DATASETS" not in tags:
        experiment_notebook = EXPERIMENT_NOTEBOOK

    if deployment_notebook is None and "DATASETS" not in tags:
        deployment_notebook = DEPLOYMENT_NOTEBOOK

    # The new task must have its own task_id, experiment_id and operator_id.
    # Notice these values are ignored when a notebook is run in a pipeline.
    # They are only used by JupyterLab interface.
    init_notebook_metadata(task_id, deployment_notebook, experiment_notebook)

    # saves new notebooks to object storage
    if "DATASETS" not in tags:
        obj_name = f"{PREFIX}/{task_id}/Experiment.ipynb"
        experiment_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"
        put_object(obj_name, dumps(experiment_notebook).encode())

        obj_name = f"{PREFIX}/{task_id}/Deployment.ipynb"
        deployment_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"
        put_object(obj_name, dumps(deployment_notebook).encode())

        # create deployment notebook and experiment_notebook on jupyter
        create_jupyter_files(task_name=name,
                             deployment_notebook=dumps(deployment_notebook).encode(),
                             experiment_notebook=dumps(experiment_notebook).encode())
    else:
        experiment_notebook_path = None
        deployment_notebook_path = None

    # saves task info to the database
    task = Task(uuid=task_id,
                name=name,
                description=description,
                tags=tags,
                image=image,
                commands=commands,
                arguments=arguments,
                experiment_notebook_path=experiment_notebook_path,
                deployment_notebook_path=deployment_notebook_path,
                is_default=is_default)
    db_session.add(task)
    db_session.commit()

    return task.as_dict()


def get_task(task_id):
    """
    Details a task from our database.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    dict
        The task attributes.

    Raises
    ------
    NotFound
        When task_id does not exist.
    """
    task = Task.query.get(task_id)

    if task is None:
        raise NOT_FOUND

    return task.as_dict()


def update_task(task_id, **kwargs):
    """
    Updates a task in our database/object storage.

    Parameters
    ----------
    task_id : str
    **kwargs:
        Arbitrary keyword arguments.

    Returns
    -------
    dict
        The task attributes.

    Raises
    ------
    NotFound
        When task_id does not exist.
    BadRequest
        When the `**kwargs` (task attributes) are invalid.
    """
    task = Task.query.get(task_id)

    if task is None:
        raise NOT_FOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != task.name:
            check_comp_name = db_session.query(Task).filter_by(name=name).first()
            if check_comp_name:
                raise BadRequest("a task with that name already exists")

    if "tags" in kwargs:
        tags = kwargs["tags"]
        if any(tag not in VALID_TAGS for tag in tags):
            valid_str = ",".join(VALID_TAGS)
            raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

    if "experiment_notebook" in kwargs:
        obj_name = f"{PREFIX}/{task_id}/Experiment.ipynb"
        put_object(obj_name, dumps(kwargs["experiment_notebook"]).encode())
        del kwargs["experiment_notebook"]

    if "deployment_notebook" in kwargs:
        obj_name = f"{PREFIX}/{task_id}/Deployment.ipynb"
        put_object(obj_name, dumps(kwargs["deployment_notebook"]).encode())
        del kwargs["deployment_notebook"]

    # store the name to use it after update
    old_name = task.name

    try:
        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)
        db_session.query(Task).filter_by(uuid=task_id).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    # update jupyter folder name if name changed
    if old_name != task.name:
        update_folder_name(f"{PREFIX}/{old_name}", f"{PREFIX}/{task.name}")

    return task.as_dict()


def delete_task(task_id):
    """
    Delete a task in our database/object storage.

    Parameters
    ----------
    task_id : str

    Returns
    -------
    dict
        The deletion result.

    Raises
    ------
    NotFound
        When task_id does not exist.
    """
    task = Task.query.get(task_id)

    if task is None:
        raise NOT_FOUND

    try:
        db_session.query(Task).filter_by(uuid=task_id).delete()

        # remove files and directory from jupyter notebook server
        source_name = f"{PREFIX}/{task.name}"
        jupyter_files = list_files(source_name)
        if jupyter_files is not None:
            for jupyter_file in jupyter_files["content"]:
                delete_file(jupyter_file["path"])
            delete_file(source_name)

        # remove MinIO files and directory
        source_name = f"{PREFIX}/{task_id}"
        minio_files = list_objects(source_name)
        for minio_file in minio_files:
            remove_object(minio_file.object_name)
        remove_object(source_name)

        db_session.commit()
    except IntegrityError as e:
        raise Forbidden(str(e))
    except (InvalidRequestError, ProgrammingError, ResponseError) as e:
        raise BadRequest(str(e))

    return {"message": "Task deleted"}


def copy_task(name, description, tags, copy_from):
    """
    Makes a copy of a task in our database/object storage.

    Parameters
    ----------
    name : str
    description : str
    tags : list
        The task tags list.
    copy_from : str
        The task_id from which the notebooks are copied.

    Returns
    -------
    dict
        The task attributes.

    Raises
    ------
    BadRequest
        When copy_from does not exist.
    """
    task = Task.query.get(copy_from)

    if task is None:
        raise BadRequest("Source task does not exist")

    task_id = uuid_alpha()
    image = task.image
    commands = task.commands
    arguments = task.arguments

    # reads source notebooks from object storage
    source_name = f"{PREFIX}/{copy_from}/Deployment.ipynb"
    deployment_notebook = loads(get_object(source_name))

    source_name = f"{PREFIX}/{copy_from}/Experiment.ipynb"
    experiment_notebook = loads(get_object(source_name))

    # Even though we are creating copies, the new task must have
    # its own task_id, experiment_id and operator_id.
    # We don't want to mix models and metrics of different tasks.
    # Notice these values are ignored when a notebook is run in a pipeline.
    # They are only used by JupyterLab interface.
    init_notebook_metadata(task_id, deployment_notebook, experiment_notebook)

    # saves new notebooks to object storage
    destination_name = f"{PREFIX}/{task_id}/Deployment.ipynb"
    deployment_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    put_object(destination_name, dumps(deployment_notebook).encode())

    destination_name = f"{PREFIX}/{task_id}/Experiment.ipynb"
    experiment_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    put_object(destination_name, dumps(experiment_notebook).encode())

    # create deployment notebook and eperiment notebook on jupyter
    create_jupyter_files(task_name=name,
                         deployment_notebook=dumps(deployment_notebook).encode(),
                         experiment_notebook=dumps(experiment_notebook).encode())

    # saves task info to the database
    task = Task(uuid=task_id,
                name=name,
                description=description,
                tags=tags,
                image=image,
                commands=commands,
                arguments=arguments,
                deployment_notebook_path=deployment_notebook_path,
                experiment_notebook_path=experiment_notebook_path,
                is_default=False)
    db_session.add(task)
    db_session.commit()

    return task.as_dict()


def create_jupyter_files(task_name, deployment_notebook, experiment_notebook):
    """
    Creates jupyter notebook files on jupyter server.

    Parameters
    ----------
    task_name : str
    deployment_notebook : bytes
        The notebook content.
    experiment_notebook : bytes
        The notebook content.
    """
    # always try to create tasks folder to guarantee its existence
    create_new_file(PREFIX, is_folder=True)

    path = f"{PREFIX}/{task_name}"
    create_new_file(path=path, is_folder=True)

    if deployment_notebook is not None:
        deployment_notebook_path = join(path, "Deployment.ipynb")
        create_new_file(path=deployment_notebook_path,
                        is_folder=False,
                        content=deployment_notebook)

    if experiment_notebook is not None:
        experiment_notebook_path = join(path, "Experiment.ipynb")
        create_new_file(path=experiment_notebook_path,
                        is_folder=False,
                        content=experiment_notebook)


def init_notebook_metadata(task_id, deployment_notebook, experiment_notebook):
    """
    Sets random experiment_id and operator_id to notebooks metadata.
    Dicts are passed by reference, so no need to return.

    Parameters
    ----------
    task_id : str
    deployment_notebook : dict
    experiment_notebook : dict
    """
    experiment_id = uuid_alpha()
    operator_id = uuid_alpha()

    # sets these values to notebooks
    if deployment_notebook is not None:
        deployment_notebook["metadata"]["experiment_id"] = experiment_id
        deployment_notebook["metadata"]["operator_id"] = operator_id
        deployment_notebook["metadata"]["task_id"] = task_id
    if experiment_notebook is not None:
        experiment_notebook["metadata"]["experiment_id"] = experiment_id
        experiment_notebook["metadata"]["operator_id"] = operator_id
        experiment_notebook["metadata"]["task_id"] = task_id


def raise_if_invalid_docker_image(image):
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
