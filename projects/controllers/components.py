# -*- coding: utf-8 -*-
"""Components controller."""
from datetime import datetime
from os.path import join
from pkgutil import get_data

from minio.error import ResponseError
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound


from ..database import db_session
from ..jupyter import create_new_file, set_workspace, list_files, delete_file
from ..models import Component
from ..object_storage import BUCKET_NAME, get_object, put_object, \
    duplicate_object, list_objects, remove_object
from .utils import uuid_alpha

PREFIX = "components"
VALID_TAGS = ["DEFAULT", "FEATURE_ENGINEERING", "PREDICTOR"]
TRAINING_NOTEBOOK = get_data("projects", "config/Training.ipynb")
INFERENCE_NOTEBOOK = get_data("projects", "config/Inference.ipynb")


def list_components():
    """Lists all components from our database.

    Returns:
        A list of all components.
    """
    components = Component.query.all()
    return [component.as_dict() for component in components]


def create_component(name=None, description=None, tags=None,
                     training_notebook=None, inference_notebook=None,
                     is_default=False, copy_from=None, **kwargs):
    """Creates a new component in our database/object storage.

    Args:
        name (str): the component name.
        tags (list): the list of tags.
        training_notebook (str, optional): the notebook content.
        inference_notebook (str, optional): the notebook content.
        is_default (bool, optional): whether it is a built-in component.
        copy_from (str, optional): the component to copy the notebooks from.

    Returns:
        The component info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    if copy_from and (training_notebook or inference_notebook):
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
    if training_notebook is None:
        training_notebook = TRAINING_NOTEBOOK

    # adds notebook to object storage
    obj_name = f"{PREFIX}/{component_id}/Training.ipynb"
    put_object(obj_name, training_notebook)

    # formats the notebook path (will save the path to database)
    training_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"

    # repeat the steps above for the inference notebook
    if inference_notebook is None:
        inference_notebook = INFERENCE_NOTEBOOK
    obj_name = f"{PREFIX}/{component_id}/Inference.ipynb"
    put_object(obj_name, inference_notebook)
    inference_notebook_path = f"minio://{BUCKET_NAME}/{obj_name}"

    # create inference notebook and training_notebook on jupyter
    create_jupyter_files(component_id, inference_notebook, training_notebook)

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          description=description,
                          tags=tags,
                          training_notebook_path=training_notebook_path,
                          inference_notebook_path=inference_notebook_path,
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

        db_session.query(Component).filter_by(uuid=uuid).delete()
        db_session.commit()
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

    # adds notebooks to object storage
    source_name = f"{PREFIX}/{copy_from}/Training.ipynb"
    destination_name = f"{PREFIX}/{component_id}/Training.ipynb"
    duplicate_object(source_name, destination_name)
    training_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    training_notebook = get_object(source_name)

    source_name = f"{PREFIX}/{copy_from}/Inference.ipynb"
    destination_name = f"{PREFIX}/{component_id}/Inference.ipynb"
    duplicate_object(source_name, destination_name)
    inference_notebook_path = f"minio://{BUCKET_NAME}/{destination_name}"
    inference_notebook = get_object(source_name)

    # create inference notebook and training_notebook on jupyter
    create_jupyter_files(component_id, inference_notebook, training_notebook)

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          description=description,
                          tags=tags,
                          training_notebook_path=training_notebook_path,
                          inference_notebook_path=inference_notebook_path,
                          is_default=False)
    db_session.add(component)
    db_session.commit()

    return component.as_dict()


def create_jupyter_files(component_id, inference_notebook, training_notebook):
    """Creates jupyter notebook files on jupyter server.

    Args:
        component_id (str): the component uuid.
        inference_notebook (str): the notebook content.
        training_notebook (str): the notebook content.
    """
    # always try to create components folder to guarantee its existence
    create_new_file(PREFIX, is_folder=True)

    path = f"{PREFIX}/{component_id}"
    create_new_file(path=path, is_folder=True)

    inference_notebook_path = join(path, "Inference.ipynb")
    create_new_file(path=inference_notebook_path,
                    is_folder=False,
                    content=inference_notebook)

    training_notebook_path = join(path, "Training.ipynb")
    create_new_file(path=training_notebook_path,
                    is_folder=False,
                    content=training_notebook)

    set_workspace(inference_notebook_path, training_notebook_path)
