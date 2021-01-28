# -*- coding: utf-8 -*-
"""Parameter controller."""
from projects import models, schemas


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
        """
        # get parameters from given operator_id
        operator = self.session.query(models.Operator).get(operator_id)
        parameters = operator.parameters

        value = parameter.dict().get("value")

        # update parameter value
        parameters[name] = value

        update_data = {"parameters": parameters}

        self.session.query(models.Operator).filter_by(uuid=operator_id).update(update_data)
        self.session.commit()

        operator = self.session.query(models.Operator).get(operator_id)

        return schemas.Operator.from_model(operator)
