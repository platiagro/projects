# -*- coding: utf-8 -*-
"""Components controller."""
from datetime import datetime
from pkgutil import get_data
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Component
from ..object_storage import BUCKET_NAME, put_object

PREFIX = "components"
EMPTY_NOTEBOOK = get_data("projects", "config/Untitled.ipynb")


def list_components():
    """Lists all components from our database.

    Returns:
        A list of all components ids.
    """
    components = Component.query.all()
    return [component.uuid for component in components]


def create_component(name=None, is_default=False, **kwargs):
    """Creates a new component in our database.

    Args:
        name (str): the component name.
        is_default (bool, optional): whether it is a builtin component.

    Returns:
        The component info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    component_id = str(uuid4())
    training_notebook = "{}/{}/Training.ipynb".format(PREFIX, component_id)
    inference_notebook = "{}/{}/Inference.ipynb".format(PREFIX, component_id)

    # Adds empty notebooks to object_storage
    put_object(training_notebook, EMPTY_NOTEBOOK)
    put_object(inference_notebook, EMPTY_NOTEBOOK)

    # prepends 'minio://BUCKET_NAME/' to the str saved to database
    training_notebook = "minio://{}/{}".format(BUCKET_NAME, training_notebook)
    inference_notebook = "minio://{}/{}".format(BUCKET_NAME, inference_notebook)

    # Saves component info to the database
    component = Component(uuid=component_id,
                          name=name,
                          training_notebook=training_notebook,
                          inference_notebook=inference_notebook,
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
    """Updates a component in our database.

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
