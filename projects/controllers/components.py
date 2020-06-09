# -*- coding: utf-8 -*-
"""Components controller."""
import re
from datetime import datetime
from json import dumps, loads
from os.path import join
from pkgutil import get_data

from minio.error import ResponseError
from sqlalchemy.exc import InvalidRequestError, IntegrityError, ProgrammingError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound


from ..database import db_session
from ..jupyter import create_new_file, set_workspace, list_files, delete_file
from ..models import Component
from ..object_storage import BUCKET_NAME, get_object, put_object, \
    list_objects, remove_object
from .utils import uuid_alpha

PREFIX = "components"
VALID_TAGS = ["DEFAULT", "FEATURE_ENGINEERING", "PREDICTOR"]
DEPLOYMENT_NOTEBOOK = loads(get_data("projects", "config/Deployment.ipynb"))
EXPERIMENT_NOTEBOOK = loads(get_data("projects", "config/Experiment.ipynb"))


def list_components():
    """Lists all components from our database.

    Returns:
        A list of all components sorted by name in natural sort order.
    """
    components = db_session.query(Component) \
        .all()
    # sort the list in place, using natural sort
    components.sort(key=lambda o: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', o.name)])
    return [component.as_dict() for component in components]


def create_component(name=None, description=None, tags=None,
                     experiment_notebook=None, deployment_notebook=None,
                     is_default=False, copy_from=None, **kwargs):
    """Creates a new component in our database/object storage.

    Args:
        name (str): the component name.
        tags (list): the list of tags.
        experiment_notebook (str, optional): the notebook content.
        deployment_notebook (str, optional): the notebook content.
        is_default (bool, optional): whether it is a built-in component.
        copy_from (str, optional): the component to copy the notebooks from.

    Returns:
        The component info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    if copy_from and (experiment_notebook or deployment_notebook):
        raise BadRequest("Either provide notebooks or a component to copy from")

    if tags is None or len(tags) == 0:
        tags = ["DEFAULT"]

    if any(tag not in VALID_TAGS for tag in tags):
        valid_str = ",".join(VALID_TAGS)
        raise BadRequest(f"Invalid tag. Choose any of {valid_str}")

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

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          description=description,
                          tags=tags,
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
        raise NotFound("The specified component does not exist")

    return component.as_dict()


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
        raise NotFound("The specified component does not exist")

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
        raise NotFound("The specified component does not exist")

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
