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

    def raise_if_operator_does_not_exist(self, operator_id: str):
        """
        Raises an exception if the specified operator does not exist.

        Parameters
        ----------
        operator_id : str

        Raises
        ------
        NotFound
        """
        operator = self.session.query(models.Operator) \
            .filter_by(uuid=operator_id)

        if operator.scalar() is None:
            raise NOT_FOUND

    def list_operators(self, project_id: str, experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
        """
        Lists all operators under an experiment.

        Parameters
        ----------
        project_id : str
        experiment_id : str or None
        deployment_id : str or None

        Returns
        -------
        projects.schemas.ListOperator
        """
        operators = self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter_by(deployment_id=deployment_id) \
            .all()

        return schemas.OperatorList.from_orm(operators, len(operators))

    def create_operator(self,
                        operator: schemas.OperatorCreate,
                        project_id: str,
                        experiment_id: Optional[str] = None,
                        deployment_id: Optional[str] = None):
        """
        Creates a new operator in our database.

        Parameters
        ----------
        operator: projects.schemas.operator.OperatorCreate
        project_id : str
        experiment_id : str or None
        deployment_id : str or None

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
            self.raise_if_dependencies_are_invalid(project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   deployment_id=deployment_id,
                                                   dependencies=operator.dependencies)

        if experiment_id and deployment_id:
            raise BadRequest("Operator cannot contain an experiment and a deployment simultaneously")

        if operator.parameters is None:
            operator.parameters = {}

        self.raise_if_parameters_are_invalid(operator.parameters)

        operator = models.Operator(uuid=uuid_alpha(),
                                   name=operator.name,
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

        return schemas.Operator.from_orm(operator)

    def update_operator(self,
                        operator: schemas.OperatorUpdate,
                        project_id: str,
                        operator_id: str,
                        experiment_id: Optional[str] = None,
                        deployment_id: Optional[str] = None,):
        """
        Updates an operator in our database and adjusts the position of others.

        Parameters
        ----------
        operator: projects.schemas.operator.OperatorUpdate
        project_id  :str
        experiment_id : str or None
        deployment_id : str or None
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
        stored_operator = self.session.query(models.Operator).get(operator_id)

        if stored_operator is None:
            raise NOT_FOUND

        if operator.dependencies is not None:
            self.raise_if_dependencies_are_invalid(project_id=project_id,
                                                   experiment_id=experiment_id,
                                                   deployment_id=deployment_id,
                                                   dependencies=operator.dependencies,
                                                   operator_id=operator_id)

        update_data = operator.dict(exclude_unset=True)

        # when parameters are updated, also updates status
        if operator.parameters is not None:
            setted_keys = set(key for key, value in operator.parameters.items() if value != "")
            all_keys = set(p["name"] for p in stored_operator.task.parameters) - {"dataset", "target"}
            status = "Setted up" if all_keys <= setted_keys else "Unset"
            update_data.update({"status": status})

        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Operator).filter_by(uuid=operator_id).update(update_data)
        self.session.commit()

        operator = self.session.query(models.Operator).get(operator_id)

        return schemas.Operator.from_orm(operator)

    def delete_operator(self,
                        project_id: str,
                        operator_id: str,
                        experiment_id: Optional[str] = None,
                        deployment_id: Optional[str] = None):
        """
        Delete an operator in our database.

        Parameters
        ----------
        project_id : str
        experiment_id : str or None
        deployment_id : str or None
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
            .filter_by(deployment_id=deployment_id) \
            .filter(models.Operator.uuid != operator_id) \
            .all()
        for op in operators:
            if operator_id in op.dependencies:
                dependencies = op.dependencies.remove(operator_id)
                if dependencies is None:
                    dependencies = []

                op_update = schemas.OperatorUpdate(
                    dependencies=dependencies,
                )
                self.update_operator(project_id=project_id,
                                     experiment_id=experiment_id,
                                     deployment_id=deployment_id,
                                     operator_id=op.uuid,
                                     operator=op_update)

        self.session.delete(operator)
        self.session.commit()

        return schemas.Message(message="Operator deleted")

    def raise_if_parameters_are_invalid(self, parameters: Dict):
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

    def raise_if_dependencies_are_invalid(self,
                                          project_id: str,
                                          dependencies: List,
                                          experiment_id: Optional[str] = None,
                                          deployment_id: Optional[str] = None,
                                          operator_id: Optional[str] = None):
        """
        Raises an exception if the specified dependencies are not valid.
        The invalid dependencies are duplicate elements on the dependencies,
        dependencies including the actual operator_id, dependencie's operator
        doesn't exist and ciclycal dependencies.

        Parameters
        ----------
        project_id : str
        dependencies : list
        experiment_id : str or None
        deployment_id : str or None
        operator_id : str or None

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
                self.raise_if_operator_does_not_exist(d)
                if d == operator_id:
                    raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)
            except NotFound:
                raise BadRequest(DEPENDENCIES_EXCEPTION_MSG)

        self.raise_if_has_cycles(
            project_id=project_id,
            experiment_id=experiment_id,
            deployment_id=deployment_id,
            operator_id=operator_id,
            dependencies=dependencies,
        )

    def raise_if_has_cycles(self,
                            project_id: str,
                            operator_id: str,
                            dependencies: List[str],
                            experiment_id: Optional[str] = None,
                            deployment_id: Optional[str] = None):
        """
        Raises an exception if the dependencies of operators from experiment are cyclical.

        Parameters
        ----------
        project_id : str
        operator_id : str
        dependencies : list or None
        experiment_id : str or None
        deployment_id : str or None

        Raises
        ------
        BadRequest
            When dependencies are cyclic.
        """
        operators = self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter_by(deployment_id=deployment_id) \
            .all()

        visited = dict.fromkeys([op.uuid for op in operators], False)
        recursion_stack = dict.fromkeys([op.uuid for op in operators], False)

        for op in operators:
            op_uuid = op.uuid
            if visited[op_uuid] is False \
               and self.has_cycles_util(op_uuid, visited, recursion_stack, dependencies, operator_id) is True:
                raise BadRequest("Cyclical dependencies.")
        return False

    def has_cycles_util(self,
                        operator_id: str,
                        visited: Dict[str, bool],
                        recursion_stack: Dict[str, bool],
                        new_dependencies: List[str],
                        new_dependencies_op: str):
        """
        Check if a run has cycle.

        Parameters
        ----------
        operator_id : str
        visited : dict
        recursion_stack : dict
        new_dependencies : list
        new_dependencies_op : str

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
            if ((visited.get(neighbour) is False and
                 self.has_cycles_util(neighbour, visited, recursion_stack, new_dependencies, new_dependencies_op) is True) or
                    recursion_stack.get(neighbour) is True):
                return True

        recursion_stack[operator_id] = False
        return False
