# -*- coding: utf-8 -*-
"""Components controller."""
from datetime import datetime
from pkgutil import get_data
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from .jupyter import create_new_file, set_workspace

from ..database import db_session
from ..models import Component
from ..object_storage import BUCKET_NAME, get_object, put_object, duplicate_object

PREFIX = "components"
TRAINING_NOTEBOOK = get_data("projects", "config/Training.ipynb")
INFERENCE_NOTEBOOK = get_data("projects", "config/Inference.ipynb")


def list_components():
    """Lists all components from our database.

    Returns:
        A list of all components ids.
    """
    components = Component.query.all()
    return components


def create_component(name=None, training_notebook=None, inference_notebook=None,
                     is_default=False, copy_from=None, **kwargs):
    """Creates a new component in our database/object storage.

    Args:
        name (str): the component name.
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

    # creates a component with specified name,
    # but copies notebooks from a source component
    if copy_from:
        return copy_component(name, copy_from)

    component_id = str(uuid4())

    # loads a sample notebook if none was sent
    if training_notebook is None:
        training_notebook = TRAINING_NOTEBOOK

    # adds notebook to object storage
    obj_name = "{}/{}/Training.ipynb".format(PREFIX, component_id)
    put_object(obj_name, training_notebook)

    # formats the notebook path (will save the path to database)
    training_notebook_path = "minio://{}/{}".format(BUCKET_NAME, obj_name)

    # repeat the steps above for the inference notebook
    if inference_notebook is None:
        inference_notebook = INFERENCE_NOTEBOOK
    obj_name = "{}/{}/Inference.ipynb".format(PREFIX, component_id)
    put_object(obj_name, inference_notebook)
    inference_notebook_path = "minio://{}/{}".format(BUCKET_NAME, obj_name)

    # create inference notebook and training_notebook on jupyter
    create_jupyter_files(component_id, inference_notebook, training_notebook)

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
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

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Component).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return component.as_dict()


def copy_component(name, copy_from):
    """Makes a copy of a component in our database/object storage.

    Args:
        name (str): the component name.
        copy_from (str, optional): the component_id from which the notebooks are copied.

    Returns:
        The component info.
    """
    component = Component.query.get(copy_from)

    if component is None:
        raise BadRequest("Source component does not exist")

    component_id = str(uuid4())

    # adds notebooks to object storage
    source_name = "{}/{}/Training.ipynb".format(PREFIX, copy_from)
    destination_name = "{}/{}/Training.ipynb".format(PREFIX, component_id)
    duplicate_object(source_name, destination_name)
    training_notebook_path = "minio://{}/{}".format(BUCKET_NAME, destination_name)
    training_notebook = get_object(source_name)

    source_name = "{}/{}/Inference.ipynb".format(PREFIX, copy_from)
    destination_name = "{}/{}/Inference.ipynb".format(PREFIX, component_id)
    duplicate_object(source_name, destination_name)
    inference_notebook_path = "minio://{}/{}".format(BUCKET_NAME, destination_name)
    inference_notebook = get_object(source_name)

    # create inference notebook and training_notebook on jupyter
    create_jupyter_files(component_id, inference_notebook, training_notebook)

    # saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          training_notebook_path=training_notebook_path,
                          inference_notebook_path=inference_notebook_path,
                          is_default=False)
    db_session.add(component)
    db_session.commit()
    return component.as_dict()


def create_jupyter_files(component_id, inference_notebook, training_notebook):
    # always try to create components folder to guarantee his existence
    create_new_file("", PREFIX, True)

    path = "{}/{}".format(PREFIX, component_id)
    create_new_file(PREFIX, component_id, True)
    create_new_file(path, "Inference.ipynb", False, inference_notebook)
    create_new_file(path, "Training.ipynb", False, training_notebook)
    set_workspace(path, "Inference.ipynb", "Training.ipynb")