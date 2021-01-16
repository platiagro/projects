# -*- coding: utf-8 -*-
"""Operator controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.tasks import TaskController
from projects.controllers.utils import uuid_alpha
from projects.models import Operator

PARAMETERS_EXCEPTION_MSG = "The specified parameters are not valid"
DEPENDENCIES_EXCEPTION_MSG = "The specified dependencies are not valid."


class OperatorController:
    def __init__(self, session):
        self.session = session
        self.task_controller = TaskController(session)

    def raise_if_operator_does_not_exist(self, operator_id, experiment_id=None):
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
        operator = self.session.query(Operator) \
            .filter_by(uuid=operator_id)

        if operator.scalar() is None:
            raise NotFound("The specified operator does not exist")
        else:
            # verify if operator is from the provided experiment
            if experiment_id and operator.one().experiment_id != experiment_id:
                raise NotFound("The specified operator is from another experiment")

    def list_operators(self, project_id, experiment_id):
        """
        Lists all operators under an experiment.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        list
            A list of all operators.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        operators = self.session.query(Operator) \
            .filter_by(experiment_id=experiment_id) \
            .all()

        return operators

    def create_operator(self, project_id, experiment_id=None, deployment_id=None,
                        task_id=None, parameters=None, dependencies=None,
                        position_x=None, position_y=None, **kwargs):
        """
        Creates a new operator in our database.
        The new operator is added to the end of the operator list.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        task_id :str
        parameters : dict
            The parameters dict.
        dependencies : list
            The dependencies array.
        position_x : float
            Position x.
        position_y : float
            Position y.
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The operator attributes.

        Raises
        ------
        BadRequest
            When task_id is not a str instance.
            When the `**kwargs` (task attributes) are invalid.
        NotFound
            When either project_id or experiment_id does not exist.
        """
        if dependencies is None:
            dependencies = []

        if experiment_id:
            self.raise_if_dependencies_are_invalid(project_id, experiment_id, dependencies)

        if experiment_id and deployment_id:
            raise BadRequest("Operator cannot contain an experiment and a deployment simultaneously")

        if not isinstance(task_id, str):
            raise BadRequest("taskId is required")

        try:
            self.task_controller.raise_if_task_does_not_exist(task_id)
        except NotFound as e:
            raise BadRequest(e.description)

        if parameters is None:
            parameters = {}

        self.raise_if_parameters_are_invalid(parameters)

        operator = Operator(uuid=uuid_alpha(),
                            experiment_id=experiment_id,
                            deployment_id=deployment_id,
                            task_id=task_id,
                            dependencies=dependencies,
                            parameters=parameters,
                            position_x=position_x,
                            position_y=position_y)
        self.session.add(operator)

        return operator

    def update_operator(self, project_id, experiment_id, operator_id, **kwargs):
        """
        Updates an operator in our database and adjusts the position of others.

        Parameters
        ----------
        project_id  :str
        experiment_id : str
        operator_id : str
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The operator attributes.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, or operator_id does not exist.
        BadRequest
            When the `**kwargs` (task attributes) are invalid.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        operator = self.session.query(Operator).get(operator_id)

        if operator is None:
            raise NotFound("The specified operator does not exist")

        self.raise_if_parameters_are_invalid(kwargs.get("parameters", {}))

        dependencies = kwargs.get("dependencies")
        if dependencies is not None:
            self.raise_if_dependencies_are_invalid(project_id, experiment_id, dependencies, operator_id=operator_id)

        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)

        try:
            self.session.query(Operator).filter_by(uuid=operator_id).update(data)
        except (InvalidRequestError, ProgrammingError) as e:
            raise BadRequest(str(e))

        return operator

    def delete_operator(self, project_id, experiment_id, operator_id):
        """
        Delete an operator in our database.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        operator_id : str

        Returns
        -------
        dict
            The deletion result.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, or operator_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        operator = self.session.query(Operator).get(operator_id)

        if operator is None:
            raise NotFound("The specified operator does not exist")

        # check if other operators contains the operator being deleted
        # in dependencies and remove this operator from dependencies
        operators = self.session.query(Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter(Operator.uuid != operator_id) \
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

        return {"message": "Operator deleted"}

    def raise_if_parameters_are_invalid(self, parameters):
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

    def raise_if_dependencies_are_invalid(self, project_id, experiment_id, dependencies, operator_id=None):
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

    def raise_if_has_cycles(self, project_id, experiment_id, operator_id, dependencies):
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

    def has_cycles_util(self, operator_id, visited, recursion_stack, new_dependencies, new_dependencies_op):
        """
        Check if a run has cycle.

        Parameters
        ----------
        operator_id : str
        visited : bool
        recursion_stack : list
        new_dependencies :
        new_dependencies_op :

        Returns
        -------
        bool
            If a run has cycles or not.
        """
        visited[operator_id] = True
        recursion_stack[operator_id] = True

        operator = self.session.query(Operator).get(operator_id)
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
