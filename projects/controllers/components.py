# -*- coding: utf-8 -*-
"""Components controller."""
import re
from datetime import datetime
from json import dumps, loads
from os.path import join
from pkgutil import get_data

from minio.error import ResponseError
from sqlalchemy import func
from sqlalchemy import asc, desc, text
from sqlalchemy.exc import InvalidRequestError, IntegrityError, ProgrammingError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound


from ..database import db_session
from ..jupyter import create_new_file, set_workspace, list_files, delete_file
from ..models import Component
from ..object_storage import BUCKET_NAME, get_object, put_object, \
    list_objects, remove_object
from .utils import uuid_alpha, text_to_list

PREFIX = "components"
VALID_TAGS = ["DATASETS", "DEFAULT", "DESCRIPTIVE_STATISTICS", "FEATURE_ENGINEERING", "PREDICTOR"]
DEPLOYMENT_NOTEBOOK = loads(get_data("projects", "config/Deployment.ipynb"))
EXPERIMENT_NOTEBOOK = loads(get_data("projects", "config/Experiment.ipynb"))

NOT_FOUND = NotFound("The specified component does not exist")
NOT_BAD_REQUEST = BadRequest('It was not possible to sort with the specified parameter')


def create_component(**kwargs):
    """Creates a new component in our database/object storage.

    Args:
        **kwargs: arbitrary keyword arguments.

    Returns:
        The component info.
    """
    name = kwargs.get('name', None)
    description = kwargs.get('description', None)
    tags = kwargs.get('tags', None)
    commands = kwargs.get('commands', None)
    image = kwargs.get('image', None)
    experiment_notebook = kwargs.get('experiment_notebook', None)
    deployment_notebook = kwargs.get('deployment_notebook', None)
    is_default = kwargs.get('is_default', None)
    copy_from = kwargs.get('copy_from', None)

    if not isinstance(name, str):
        raise BadRequest("name is required")

    if copy_from and (experiment_notebook or deployment_notebook):
        raise BadRequest("Either provide notebooks or a component to copy from")

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

    check_comp_name = db_session.query(Component).filter_by(name=name).first()
    if check_comp_name:
        raise BadRequest("a component with that name already exists")

    # creates a component with specified name,
    # but copies notebooks from a source component
    if copy_from:
        return copy_component(name, description, tags, copy_from)

    component_id = str(uuid_alpha())

    # loads a sample notebook if none was sent
    if experiment_notebook is None:
        experiment_notebook = EXPERIMENT_NOTEBOOK

    if deployment_notebook is None:
        deployment_notebook = DEPLOYMENT_NOTEBOOK

    # The new component must have its own experiment_id and operator_id.
    # Notice these values are ignored when a notebook is run in a pipeline.
    # They are only used by JupyterLab interface.
    init_notebook_metadata(deployment_notebook, experiment_notebook)

    # saves new notebooks to object storage
    obj_name = f"{PREFIX}/{component_id}/Deployment.ipynb"
    deployment_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"
    put_object(obj_name, dumps(deployment_notebook).encode())

    obj_name = f"{PREFIX}/{component_id}/Experiment.ipynb"
    experiment_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"
    put_object(obj_name, dumps(experiment_notebook).encode())

    # create deployment notebook and experiment_notebook on jupyter
    create_jupyter_files(component_id=component_id,
                         deployment_notebook=dumps(deployment_notebook).encode(),
                         experiment_notebook=dumps(experiment_notebook).encode())

    # create the commands to be executed on pipelines
    if commands is None or len(commands) == 0:
        commands = ['''from platiagro import download_dataset;
                    download_dataset("$dataset", "$TRAINING_DATASETS_DIR/$dataset");''']
        if "DATASETS" not in tags:
            commands = [f'''papermill {experiment_notebook_path} output.ipynb -b $parameters;
                        status=$?;
                        bash upload-to-jupyter.sh $experimentId $operatorId Experiment.ipynb;
                        exit $status''']

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          description=description,
                          tags=tags,
                          commands=commands,
                          image=image,
                          experiment_notebook_path=experiment_notebook_path,
                          deployment_notebook_path=deployment_notebook_path,
                          is_default=is_default)
    db_session.add(component)
    db_session.commit()

    return component.as_dict()


def get_component(uuid):
    """Details a component from our database.

    Args:
        uuid (str): the component uuid to look for in our database.

    Returns:
        The component info.
    """
    component = Component.query.get(uuid)

    if component is None:
        raise NOT_FOUND

    return component.as_dict()


def get_components_by_tag(tag):
    """Get all components with a specific tag.

    Returns:
        A list of components.
    """
    components = db_session.query(Component).filter(Component.tags.contains([tag])).all()
    return [component.as_dict() for component in components]


def update_component(uuid, **kwargs):
    """Updates a component in our database/object storage.

    Args:
        uuid (str): the component uuid to look for in our database.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The component info.
    """
    component = Component.query.get(uuid)

    if component is None:
        raise NOT_FOUND

    if "name" in kwargs:
        name = kwargs["name"]
        if name != component.name:
            check_comp_name = db_session.query(Component).filter_by(name=name).first()
            if check_comp_name:
                raise BadRequest("a component with that name already exists")

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

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Component).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return component.as_dict()


def delete_component(uuid):
    """Delete a component in our database/object storage.

    Args:
        uuid (str): the component uuid to look for in our database.

    Returns:
        The component info.
    """
    component = Component.query.get(uuid)

    if component is None:
        raise NOT_FOUND

    try:
        source_name = f"{PREFIX}/{uuid}"

        db_session.query(Component).filter_by(uuid=uuid).delete()

        # remove files and directory from jupyter notebook server
        jupyter_files = list_files(source_name)
        if jupyter_files is not None:
            for jupyter_file in jupyter_files["content"]:
                delete_file(jupyter_file["path"])
            delete_file(source_name)

        # remove MinIO files and directory
        minio_files = list_objects(source_name)
        for minio_file in minio_files:
            remove_object(minio_file.object_name)
        remove_object(source_name)

        db_session.commit()
    except IntegrityError as e:
        raise Forbidden(str(e))
    except (InvalidRequestError, ProgrammingError, ResponseError) as e:
        raise BadRequest(str(e))

    return {"message": "Component deleted"}


def copy_component(name, description, tags, copy_from):
    """Makes a copy of a component in our database/object storage.

    Args:
        name (str): the component name.
        description (str): the component description.
        tags (list): the component tags list.
        copy_from (str): the component_id from which the notebooks are copied.

    Returns:
        The component info.
    """
    component = Component.query.get(copy_from)

    if component is None:
        raise BadRequest("Source component does not exist")

    component_id = uuid_alpha()

    # reads source notebooks from object storage
    source_name = f"{PREFIX}/{copy_from}/Deployment.ipynb"
    deployment_notebook = loads(get_object(source_name))

    source_name = f"{PREFIX}/{copy_from}/Experiment.ipynb"
    experiment_notebook = loads(get_object(source_name))

    # Even though we are creating 'copies', the new component must have
    # its own experiment_id and operator_id. We don't want to mix models and
    # metrics of different components.
    # Notice these values are ignored when a notebook is run in a pipeline.
    # They are only used by JupyterLab interface.
    init_notebook_metadata(deployment_notebook, experiment_notebook)

    # saves new notebooks to object storage
    destination_name = f"{PREFIX}/{component_id}/Deployment.ipynb"
    deployment_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    put_object(destination_name, dumps(deployment_notebook).encode())

    destination_name = f"{PREFIX}/{component_id}/Experiment.ipynb"
    experiment_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    put_object(destination_name, dumps(experiment_notebook).encode())

    # create deployment notebook and eperiment notebook on jupyter
    create_jupyter_files(component_id=component_id,
                         deployment_notebook=dumps(deployment_notebook).encode(),
                         experiment_notebook=dumps(experiment_notebook).encode())

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          description=description,
                          tags=tags,
                          deployment_notebook_path=deployment_notebook_path,
                          experiment_notebook_path=experiment_notebook_path,
                          is_default=False)
    db_session.add(component)
    db_session.commit()

    return component.as_dict()


def create_jupyter_files(component_id, deployment_notebook, experiment_notebook):
    """Creates jupyter notebook files on jupyter server.

    Args:
        component_id (str): the component uuid.
        deployment_notebook (bytes): the notebook content.
        experiment_notebook (bytes): the notebook content.
    """
    # always try to create components folder to guarantee its existence
    create_new_file(PREFIX, is_folder=True)

    path = f"{PREFIX}/{component_id}"
    create_new_file(path=path, is_folder=True)

    deployment_notebook_path = join(path, "Deployment.ipynb")
    create_new_file(path=deployment_notebook_path,
                    is_folder=False,
                    content=deployment_notebook)

    experiment_notebook_path = join(path, "Experiment.ipynb")
    create_new_file(path=experiment_notebook_path,
                    is_folder=False,
                    content=experiment_notebook)

    set_workspace(deployment_notebook_path, experiment_notebook_path)


def init_notebook_metadata(deployment_notebook, experiment_notebook):
    """Sets random experiment_id and operator_id to notebooks metadata.

    Dicts are passed by reference, so no need to return.

    Args:
        deployment_notebook (dict): the deployment notebook content.
        experiment_notebook (dict): the experiment notebook content.
    """
    experiment_id = uuid_alpha()
    operator_id = uuid_alpha()

    # sets these values to notebooks
    deployment_notebook["metadata"]["experiment_id"] = experiment_id
    deployment_notebook["metadata"]["operator_id"] = operator_id
    experiment_notebook["metadata"]["experiment_id"] = experiment_id
    experiment_notebook["metadata"]["operator_id"] = operator_id


def pagination_components(name, page, page_size, order):
    """ Component Paging.

    Args:
        name(str):
        page(int):
        page_size(int):
        order(str):

    Returns:
        List of projects
    """
    """The numbers of items to return maximum 100 """
    query = db_session.query(Component)
    if name:
        query = query.filter(Component.name.ilike(func.lower(f"%{name}%")))
    if page == 0 and order is None:
        query = query.order_by(Component.name)
    elif page and order is None:
        query = query.order_by(text('name')).limit(page_size).offset((page - 1) * page_size)
    else:
        query = pagination_ordering(query, page_size, page, order)
    projects = query.all()
    return [project.as_dict() for project in projects]


def total_rows_components(name):
    """Counts the total number of records.

    Args:
        name(str): name

    Returns:
        rows

    """
    query = db_session.query(func.count(Component.uuid))
    if name:
        query = query.filter(Component.name.ilike(func.lower(f"%{name}%")))
    rows = query.scalar()
    return rows


def pagination_ordering(query, page_size, page, order_by):
    """Pagination ordering.

    Args:
        query (query): the project uuid.
        page(int): page number
        page_size(int) : record numbers
        order_by(str): order by

    Returns:
        query

    """
    try:
        order = text_to_list(order_by)
        if page:
            if 'asc' == order[1].lower():
                query = query.order_by(asc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
            if 'desc' == order[1].lower():
                query = query.order_by(desc(text(order[0]))).limit(page_size).offset((page - 1) * page_size)
        else:
            query = uninformed_page(query, order)
        return query
    except Exception:
        raise NOT_BAD_REQUEST


def uninformed_page(query, order):
    """If the page number was not informed just sort by the column name entered

    Args:
        query(query): query
        order(str): order

    Returns:
        query

    """
    try:
        if 'asc' == order[1].lower():
            query.order_by(asc(text(f'{order[0]}')))
        elif 'desc' == order[1].lower():
            query.order_by(desc(text(f'{order[0]}')))
        return query
    except Exception:
        raise NOT_BAD_REQUEST
