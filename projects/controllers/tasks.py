# -*- coding: utf-8 -*-
"""Tasks controller."""
import re
from datetime import datetime
from json import dumps, loads
from os.path import join
from pkgutil import get_data

from minio.error import ResponseError
from sqlalchemy import func
from sqlalchemy import asc, desc, text
from sqlalchemy.exc import InvalidRequestError, IntegrityError, ProgrammingError, OperationalError, InternalError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, InternalServerError


from projects.controllers.utils import uuid_alpha, text_to_list
from projects.database import db_session
from projects.jupyter import create_new_file, list_files, delete_file, update_folder_name
from projects.models import Task
from projects.models.task import DEFAULT_COMMANDS, DEFAULT_ARGUMENTS
from projects.object_storage import BUCKET_NAME, get_object, put_object, \
    list_objects, remove_object

PREFIX = "tasks"
VALID_TAGS = ["DATASETS", "DEFAULT", "DESCRIPTIVE_STATISTICS", "FEATURE_ENGINEERING",
              "PREDICTOR", "COMPUTER_VISION", "NLP"]
DEPLOYMENT_NOTEBOOK = loads(get_data("projects", "config/Deployment.ipynb"))
EXPERIMENT_NOTEBOOK = loads(get_data("projects", "config/Experiment.ipynb"))

NOT_FOUND = NotFound("The specified task does not exist")
BAD_REQUEST = BadRequest('It was not possible to sort with the specified parameter')


def create_task(**kwargs):
    """Creates a new task in our database/object storage.

    Args:
        **kwargs: arbitrary keyword arguments.

    Returns:
        The task info.
    """
    name = kwargs.get('name', None)
    description = kwargs.get('description', None)
    tags = kwargs.get('tags', None)
    image = kwargs.get('image', None)
    commands = kwargs.get('commands', None)
    arguments = kwargs.get('arguments', None)
    experiment_notebook = kwargs.get('experiment_notebook', None)
    deployment_notebook = kwargs.get('deployment_notebook', None)
    is_default = kwargs.get('is_default', None)
    is_monitoring = kwargs.get('is_monitoring', None)
    copy_from = kwargs.get('copy_from', None)

    if not isinstance(name, str):
        raise BadRequest("name is required")

    if copy_from and (experiment_notebook or deployment_notebook):
        raise BadRequest("Either provide notebooks or a task to copy from")

    if tags is None or len(tags) == 0:
        tags = ["DEFAULT"]

    if any(tag not in VALID_TAGS for tag in tags):
        valid_str = ",".join(VALID_TAGS)
        raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

    # check if image is a valid docker image
    if image:
        pattern = re.compile('[a-z0-9.-]+([/]{1}[a-z0-9.-]+)+([:]{1}[a-z0-9.-]+){0,1}$')
        if pattern.match(image) is None:
            raise BadRequest("invalid docker image name")

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

    if commands is None or len(commands) == 0:
        commands = DEFAULT_COMMANDS

    if arguments is None or len(arguments) == 0:
        arguments = DEFAULT_ARGUMENTS

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
                is_default=is_default,
                is_monitoring=is_monitoring)
    db_session.add(task)
    db_session.commit()

    return task.as_dict()


def get_task(uuid):
    """Details a task from our database.

    Args:
        uuid (str): the task uuid to look for in our database.

    Returns:
        The task info.
    """
    task = Task.query.get(uuid)

    if task is None:
        raise NOT_FOUND

    return task.as_dict()


def get_tasks_by_tag(tag):
    """Get all tasks with a specific tag.

    Returns:
        A list of tasks.
    """
    tasks = db_session.query(Task).filter(Task.tags.contains([tag])).all()
    return [task.as_dict() for task in tasks]


def update_task(uuid, **kwargs):
    """Updates a task in our database/object storage.

    Args:
        uuid (str): the task uuid to look for in our database.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The task info.
    """
    task = Task.query.get(uuid)

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
        obj_name = f"{PREFIX}/{uuid}/Experiment.ipynb"
        put_object(obj_name, dumps(kwargs["experiment_notebook"]).encode())
        del kwargs["experiment_notebook"]

    if "deployment_notebook" in kwargs:
        obj_name = f"{PREFIX}/{uuid}/Deployment.ipynb"
        put_object(obj_name, dumps(kwargs["deployment_notebook"]).encode())
        del kwargs["deployment_notebook"]

    # store the name to use it after update
    old_name = task.name

    try:
        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)
        db_session.query(Task).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    # update jupyter folder name if name changed
    if old_name != task.name:
        update_folder_name(f"{PREFIX}/{old_name}", f"{PREFIX}/{task.name}")

    return task.as_dict()


def delete_task(uuid):
    """Delete a task in our database/object storage.

    Args:
        uuid (str): the task uuid to look for in our database.

    Returns:
        The task info.
    """
    task = Task.query.get(uuid)

    if task is None:
        raise NOT_FOUND

    try:
        db_session.query(Task).filter_by(uuid=uuid).delete()

        # remove files and directory from jupyter notebook server
        source_name = f"{PREFIX}/{task.name}"
        jupyter_files = list_files(source_name)
        if jupyter_files is not None:
            for jupyter_file in jupyter_files["content"]:
                delete_file(jupyter_file["path"])
            delete_file(source_name)

        # remove MinIO files and directory
        source_name = f"{PREFIX}/{uuid}"
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
    """Makes a copy of a task in our database/object storage.

    Args:
        name (str): the task name.
        description (str): the task description.
        tags (list): the task tags list.
        copy_from (str): the task_id from which the notebooks are copied.

    Returns:
        The task info.
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

    # Even though we are creating 'copies', the new task must have
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
    """Creates jupyter notebook files on jupyter server.

    Args:
        task_name (str): the task name.
        deployment_notebook (bytes): the notebook content.
        experiment_notebook (bytes): the notebook content.
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
    """Sets random experiment_id and operator_id to notebooks metadata.

    Dicts are passed by reference, so no need to return.

    Args:
        task_id (str): the task uuid.
        deployment_notebook (dict): the deployment notebook content.
        experiment_notebook (dict): the experiment notebook content.
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


def pagination_tasks(name, page, page_size, order):
    """Task pagination.

    Args:
        name (str): task name
        page (int): records size
        page_size (int): page number
        order (str): order by

    Raises:
        InternalServerError: MySQL error

    Returns:
        dict: query response
    """
    try:
        query = db_session.query(Task)

        if name:
            query = query.filter(Task.name.ilike(func.lower(f"%{name}%")))

        if page is not None and order is None:
            if page == 0:
                query = query.order_by(Task.name)
            else:
                query = query.order_by(text('name')).limit(page_size).offset((page - 1) * page_size)
        else:
            query = pagination_ordering(query, page_size, page, order)

        tasks = query.all()
        total_rows = total_rows_tasks(name)

        return {'total': total_rows, 'tasks': [task.as_dict() for task in tasks]}
    except (OperationalError, InternalError):
        raise InternalServerError("The service is unavailable. Try your call again.")


def total_rows_tasks(name):
    """Counts the total number of records.

    Args:
        name(str): name

    Returns:
        rows

    """
    query = db_session.query(func.count(Task.uuid))
    if name:
        query = query.filter(Task.name.ilike(func.lower(f"%{name}%")))
    rows = query.scalar()
    return rows


def pagination_ordering(query, page_size, page, order_by):
    """Pagination ordering.

    Args:
        query (string): query to be used
        page_size (int): records size
        page (int): page number
        order_by (str): order by

    Raises:
        BadRequest: the parameters are not the same as expected.

    Returns:
        list: a list of projects
    """
    order = text_to_list(order_by)

    if len(order) <= 1 or order[1] not in ["asc", "desc"]:
        raise BadRequest("It was not possible to sort with the specified parameter")

    if page:
        if 'asc' == order[1].lower():
            query = query.order_by(asc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
        if 'desc' == order[1].lower():
            query = query.order_by(desc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
    else:
        query = uninformed_page(query, order)

    return query


def uninformed_page(query, order):
    """If the page number was not informed just sort by the column name entered

    Args:
        query(query): query
        order(str): order

    Returns:
        query

    """
    if 'asc' == order[1].lower():
        query = query.order_by(asc(text(f'{order[0]}')))
    elif 'desc' == order[1].lower():
        query = query.order_by(desc(text(f'{order[0]}')))

    return query
