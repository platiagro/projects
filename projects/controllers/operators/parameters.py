# -*- coding: utf-8 -*-
"""Parameter controller."""
import json

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist, raise_if_operator_does_not_exist
from projects.database import db_session
from projects.models import Operator


def update_parameter(project_id, experiment_id, operator_id, name, value):
    """
    Updates a parameter from operator.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    name : str
    **kwargs : dict
        New parameter value.

    Returns
    -------
    dict
        The parameter attributes.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, operator_id or name does not exist.
    BadRequest
        When the `**kwargs` (parameter attributes) are invalid
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)
    raise_if_operator_does_not_exist(operator_id)

    # get parameters from given operatorId
    operator = Operator.query.get(operator_id)
    parameters = operator.as_dict().get("parameters")

    # update parameter value
    if name in parameters:
        parameters[name] = value
    else:
        raise NotFound("The specified parameter does not exist")

    try:
        db_session.query(Operator) \
            .filter_by(uuid=operator_id) \
            .update(
                {"parameters": parameters}
            )
        db_session.commit()
    except (InvalidRequestError, ProgrammingError) as e:
        raise BadRequest(str(e))

    return operator.as_dict()