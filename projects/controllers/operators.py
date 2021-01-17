# -*- coding: utf-8 -*-
"""Operator controller."""
from datetime import datetime
from typing import Dict, List, Optional

from projects import models, schemas
from projects.controllers.tasks import TaskController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, NotFound

NOT_FOUND = NotFound("The specified operator does not exist")
PARAMETERS_EXCEPTION_MSG = "The specified parameters are not valid"
DEPENDENCIES_EXCEPTION_MSG = "The specified dependencies are not valid."


class OperatorController:
    def __init__(self, session):
        self.session = session
        self.task_controller = TaskController(session)

    def raise_if_operator_does_not_exist(self, operator_id: str, experiment_id: Optional[str] = None):
        """
        Raises an exception if the specified operator does not exist.

        Parameters
        ----------
        operator_id : str
        experiment_id : str

        Raises
        ------
        NotFound
        """
        operator = self.session.query(models.Operator) \
            .filter_by(uuid=operator_id)

        if operator.scalar() is None:
            raise NOT_FOUND
        else:
            # verify if operator is from the provided experiment
            if experiment_id and operator.one().experiment_id != experiment_id:
                raise NotFound("The specified operator is from another experiment")

    def list_operators(self, project_id: str, experiment_id: str):
        """
        Lists all operators under an experiment.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        projects.schemas.ListOperator

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        operators = self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .all()

        return schemas.OperatorList.from_model(operators, len(operators))

    def create_operator(self, operator: schemas.OperatorCreate, project_id: str, experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
        """
        Creates a new operator in our database.

        Parameters
        ----------
        operator: projects.schemas.operator.OperatorCreate
        project_id : str
        experiment_id : str

        Returns
        -------
        projects.schemas.operator.Operator

        Raises
        ------
        BadRequest
            When the operator attributes are invalid.
        """
        if not isinstance(operator.task_id, str):
            raise BadRequest("taskId is required")

        try:
            self.task_controller.raise_if_task_does_not_exist(operator.task_id)
        except NotFound as e:
            raise BadRequest(e.message)

        if operator.dependencies is None:
            operator.dependencies = []

        if experiment_id:
            self.raise_if_dependencies_are_invalid(project_id, experiment_id, operator.dependencies)

        if experiment_id and deployment_id:
            raise BadRequest("Operator cannot contain an experiment and a deployment simultaneously")

        if operator.parameters is None:
            operator.parameters = {}

        self.raise_if_parameters_are_invalid(operator.parameters)

        operator = models.Operator(uuid=uuid_alpha(),
                                   experiment_id=experiment_id,
                                   deployment_id=deployment_id,
                                   task_id=operator.task_id,
                                   dependencies=operator.dependencies,
                                   parameters=operator.parameters,
                                   position_x=operator.position_x,
                                   position_y=operator.position_y)
        self.session.add(operator)
        self.session.commit()
        self.session.refresh(operator)

        return schemas.Operator.from_model(operator)

    def update_operator(self, operator: schemas.OperatorUpdate, project_id: str, experiment_id: str, operator_id: str):
        """
        Updates an operator in our database and adjusts the position of others.

        Parameters
        ----------
        operator: projects.schemas.operator.OperatorUpdate
        project_id  :str
        experiment_id : str
        operator_id : str

        Returns
        -------
        projects.schemas.operator.Operator

        Raises
        ------
        NotFound
            When operator_id does not exist.
        BadRequest
            When the operator attributes are invalid.
        """
        self.raise_if_operator_does_not_exist(operator_id)

        if operator.dependencies is not None:
            self.raise_if_dependencies_are_invalid(project_id, experiment_id, operator.dependencies, operator_id=operator_id)

        update_data = operator.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Operator).filter_by(uuid=operator_id).update(update_data)
        self.session.commit()

        operator = self.session.query(models.Operator).get(operator_id)

        return schemas.Operator.from_model(operator)

    def delete_operator(self, project_id: str, experiment_id: str, operator_id: str):
        """
        Delete an operator in our database.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        operator_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When operator_id does not exist.
        """
        operator = self.session.query(models.Operator).get(operator_id)

        if operator is None:
            raise NOT_FOUND

        # check if other operators contains the operator being deleted
        # in dependencies and remove this operator from dependencies
        operators = self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter(models.Operator.uuid != operator_id) \
            .all()
        for op in operators:
            if operator_id in op.dependencies:
                dependencies = op.dependencies.remove(operator_id)
                if dependencies is None:
                    dependencies = []
                self.update_operator(project_id=project_id,
                                     experiment_id=experiment_id,
                                     operator_id=op.uuid,
                                     dependencies=dependencies)

        self.session.delete(operator)

        return schemas.Message(message="Operator deleted")

    def raise_if_parameters_are_invalid(self, parameters: List[Dict]):
        """
        Raises an exception if the specified parameters are not valid.

        Parameters
        ----------
        parameters : dict

        Raises
        ------
        BadRequest
            When any parameter value is not str, int, float, bool, list, or dict.
        """
        if not isinstance(parameters, dict):
            raise BadRequest(PARAMETERS_EXCEPTION_MSG)

        for key, value in parameters.items():
            if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                raise BadRequest(PARAMETERS_EXCEPTION_MSG)

    def raise_if_dependencies_are_invalid(self, project_id: str, experiment_id: str, dependencies: List, operator_id: Optional[str] = None):
        """
        Raises an exception if the specified dependencies are not valid.
        The invalid dependencies are duplicate elements on the dependencies,
        dependencies including the actual operator_id, dependencie's operator
        doesn't exist and ciclycal dependencies.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        dependencies : list
        operator_id : str

        Raises
        ------
        BadRequest
            When any dependency does not exist.
            When dependencies are cyclic.
        """
        if not isinstance(dependencies, list):
            raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

        # check if dependencies has duplicates
        if len(dependencies) != len(set(dependencies)):
            raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

        for d in dependencies:
            try:
                self.raise_if_operator_does_not_exist(d, experiment_id)
                if d == operator_id:
                    raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)
            except NotFound:
                raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

        self.raise_if_has_cycles(project_id, experiment_id, operator_id, dependencies)

    def raise_if_has_cycles(self, project_id: str, experiment_id: str, operator_id: str, dependencies: List[str]):
        """
        Raises an exception if the dependencies of operators from experiment are cyclical.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        operator_id : str
        dependencies : list

        Raises
        ------
        BadRequest
            When dependencies are cyclic.
        """
        operators = self.list_operators(project_id, experiment_id)

        visited = dict.fromkeys([op['uuid'] for op in operators], False)
        recursion_stack = dict.fromkeys([op['uuid'] for op in operators], False)

        for op in operators:
            op_uuid = op["uuid"]
            if (visited[op_uuid] is False and
                    self.has_cycles_util(op_uuid, visited, recursion_stack, dependencies, operator_id) is True):
                raise BadRequest("Cyclical dependencies.")
        return False

    def has_cycles_util(self, operator_id: str, visited: bool, recursion_stack: List, new_dependencies: List[str], new_dependencies_op: List[models.Operator]):
        """
        Check if a run has cycle.

        Parameters
        ----------
        operator_id : str
        visited : bool
        recursion_stack : list
        new_dependencies : list
        new_dependencies_op : list

        Returns
        -------
        bool
            If a run has cycles or not.
        """
        visited[operator_id] = True
        recursion_stack[operator_id] = True

        operator = self.session.query(models.Operator).get(operator_id)
        dependencies = operator.dependencies

        if operator_id == new_dependencies_op:
            dependencies = dependencies + list(set(new_dependencies) - set(dependencies))

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recursion_stack then graph is cyclic
        for neighbour in dependencies:
            if ((visited[neighbour] is False and
                 self.has_cycles_util(neighbour, visited, recursion_stack, new_dependencies, new_dependencies_op) is True) or
                    recursion_stack[neighbour] is True):
                return True

        recursion_stack[operator_id] = False
        return False
