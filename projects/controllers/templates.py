# -*- coding: utf-8 -*-
"""Templates controller."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from ..database import db_session
from ..models import Template, Operator
from .utils import raise_if_experiment_does_not_exist


def list_templates():
    """Lists all templates from our database.

    Returns:
        A list of all templates.
    """
    templates = Template.query.all()
    return [template.as_dict() for template in templates]


def create_template(name=None, experiment_id=None, **kwargs):
    """Creates a new template in our database.

    Args:
        name (str): the template name.

    Returns:
        The template info.
    """
    if not isinstance(name, str):
        raise BadRequest("name is required")

    if not isinstance(experiment_id, str):
        raise BadRequest("experimentId is required")

    try:
        raise_if_experiment_does_not_exist(experiment_id)
    except NotFound as e:
        raise BadRequest(e.description)

    operators = db_session.query(Operator) \
        .filter_by(experiment_id=experiment_id) \
        .order_by(Operator.position.asc()) \
        .all()

    # JSON array order of elements are preserved,
    # so there is no need to save positions
    components = [operator.component_id for operator in operators]

    template = Template(uuid=str(uuid4()), name=name, components=components)
    db_session.add(template)
    db_session.commit()
    return template.as_dict()


def get_template(uuid):
    """Details a template from our database.

    Args:
        uuid (str): the template uuid to look for in our database.

    Returns:
        The template info.
    """
    template = Template.query.get(uuid)

    if template is None:
        raise NotFound("The specified template does not exist")

    return template.as_dict()


def update_template(uuid, **kwargs):
    """Updates a template in our database.

    Args:
        uuid (str): the template uuid to look for in our database.
        **kwargs: arbitrary keyword arguments.

    Returns:
        The template info.
    """
    template = Template.query.get(uuid)

    if template is None:
        raise NotFound("The specified template does not exist")

    data = {"updated_at": datetime.utcnow()}
    data.update(kwargs)

    try:
        db_session.query(Template).filter_by(uuid=uuid).update(data)
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return template.as_dict()


def delete_template(uuid):
    """Delete a template in our database.

    Args:
        uuid (str): the template uuid to look for in our database.

    Returns:
        The deletion result.
    """
    template = Template.query.get(uuid)

    if template is None:
        raise NotFound("The specified template does not exist")

    db_session.delete(template)
    db_session.commit()

    return {"message": "Template deleted"}
