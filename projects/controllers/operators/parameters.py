# -*- coding: utf-8 -*-
"""Parameter controller."""
from projects import models, schemas
from projects.exceptions import NotFound


class OperatorParameterController:
    def __init__(self, session):
        self.session = session

    def update_parameter(self, operator_id: str, name: str, parameter: schemas.operator.ParameterUpdate):
        """
        Updates a parameter from operator.

        Parameters
        ----------
        operator_id : str
        name : str
        operator: schemas.operator.OperatorUpdate

        Returns
        -------
        projects.schemas.operator.ParameterUpdate

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, operator_id or name does not exist.
        BadRequest
            When the `**kwargs` (parameter attributes) are invalid
        """
        # get parameters from given operator_id
        operator = self.session.query(models.Operator).get(operator_id)
        parameters = operator.parameters

        value = parameter.dict().get("value")

        # update parameter value
        if name in parameters:
            parameters[name] = value
        else:
            raise NotFound("The specified parameter does not exist")

        update_data = {"parameters": parameters}

        self.session.query(models.Operator).filter_by(uuid=operator_id).update(update_data)
        self.session.commit()

        operator = self.session.query(models.Operator).get(operator_id)

        return schemas.Operator.from_model(operator)
