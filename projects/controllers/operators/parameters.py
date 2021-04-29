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
        parameter: schemas.operator.ParameterUpdate

        Returns
        -------
        projects.schemas.operator.Operator
        """
        # get parameters from given operator_id
        operator = self.session.query(models.Operator).get(operator_id)
        parameters = operator.parameters

        value = parameter.dict().get("value")

        # update parameter value
        parameters[name] = value

        update_data = {"parameters": parameters}

        setted_keys = set(key for key, value in parameters.items() if value != "")
        all_keys = set(p["name"] for p in operator.task.parameters) - {"dataset", "target"}
        status = "Setted up" if all_keys <= setted_keys else "Unset"
        update_data.update({"status": status})

        self.session.query(models.Operator).filter_by(uuid=operator_id).update(update_data)
        self.session.commit()

        operator = self.session.query(models.Operator).get(operator_id)

        return schemas.Operator.from_orm(operator)
