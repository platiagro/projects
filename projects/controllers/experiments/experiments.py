# -*- coding: utf-8 -*-
"""Experiments controller."""
import sys
from datetime import datetime
from os.path import join

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.operators import OperatorController
from projects.controllers.utils import uuid_alpha
from projects.models import Comparison, Deployment, Experiment, Operator, Template
from projects.object_storage import remove_objects


NOT_FOUND = NotFound("The specified experiment does not exist")


class ExperimentController:
    def __init__(self, session):
        self.session = session
        self.operator_controller = OperatorController(session)

    def raise_if_experiment_does_not_exist(self, experiment_id):
        """
        Raises an exception if the specified experiment does not exist.

        Parameters
        ----------
        experiment_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(Experiment.uuid) \
            .filter_by(uuid=experiment_id) \
            .scalar() is not None

        if not exists:
            raise NotFound("The specified experiment does not exist")

    def list_experiments(self, project_id):
        """
        Lists all experiments under a project.

        Parameters
        ----------
        project_id: str

        Returns
        -------
        list
            A list of all experiments.

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        experiments = self.session.query(Experiment) \
            .filter_by(project_id=project_id) \
            .order_by(Experiment.position.asc()) \
            .all()
        return experiments

    def create_experiment(self, project_id=None, name=None, copy_from=None):
        """
        Creates a new experiment in our database and adjusts the position of others.
        The new experiment is added to the end of the experiment list.

        Parameters
        ----------
        project_id : str
        name : str
        copy_from : str
            The experiment id from which uuid.

        Returns
        -------
        dict
            The experiment attributes.

        Raises
        ------
        NotFound
            When project_id does not exist.
        BadRequest
            When name is not a str instance.
            When name is already the name of another experiment.
        """
        if not isinstance(name, str):
            raise BadRequest("name is required")

        check_experiment_name = self.session.query(Experiment) \
            .filter(Experiment.project_id == project_id) \
            .filter(Experiment.name == name) \
            .first()
        if check_experiment_name:
            raise BadRequest("an experiment with that name already exists")

        experiment = Experiment(uuid=uuid_alpha(), name=name, project_id=project_id)
        self.session.add(experiment)

        if copy_from:
            try:
                experiment_find = self.find_by_experiment_id(experiment_id=copy_from)

                source_operators = {}
                for source_operator in experiment_find["operators"]:

                    source_dependencies = source_operator["dependencies"]

                    kwargs = {
                        "task_id": source_operator["taskId"],
                        "parameters": source_operator["parameters"],
                        "dependencies": [],
                        "position_x": source_operator["positionX"],
                        "position_y": source_operator["positionY"]
                    }
                    operator = self.operator_controller.create_operator(project_id=project_id,
                                                                        experiment_id=experiment.uuid,
                                                                        **kwargs)

                    source_operators[source_operator["uuid"]] = {
                        "copy_uuid": operator["uuid"],
                        "dependencies": source_dependencies
                    }

                # update dependencies on new operators
                for _, value in source_operators.items():
                    dependencies = [source_operators[d]["copy_uuid"] for d in value["dependencies"]]
                    self.operator_controller.update_operator(project_id=project_id,
                                                             experiment_id=experiment.uuid,
                                                             operator_id=value["copy_uuid"],
                                                             dependencies=dependencies)

            except NotFound:
                self.delete_experiment(project_id=project_id,
                                       experiment_id=experiment.uuid)
                raise BadRequest("Source experiment does not exist")

        self.session.flush()
        self.fix_positions(project_id=project_id,
                           experiment_id=experiment.uuid,
                           new_position=sys.maxsize)  # will add to end of list

        return experiment

    def get_experiment(self, project_id, experiment_id):
        """
        Details an experiment from our database.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        dict
            The experiment attributes.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        experiment = self.session.query(Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        return experiment

    def update_experiment(self, project_id, experiment_id, **kwargs):
        """
        Updates an experiment in our database and adjusts the position of others.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        **kwargs:
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The experiment attributes.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        BadRequest
            When name is already the name of another experiment.
            When `kwargs["template_id"]` is informed but it does not exist.
        """
        self.raise_if_experiment_does_not_exist(experiment_id)

        experiment = self.session.query(Experiment).get(experiment_id)

        if "name" in kwargs:
            name = kwargs["name"]
            if name != experiment.name:
                check_experiment_name = self.session.query(Experiment) \
                    .filter(Experiment.project_id == project_id) \
                    .filter(Experiment.name == name) \
                    .first()
                if check_experiment_name:
                    raise BadRequest("an experiment with that name already exists")

        # updates operators
        if "template_id" in kwargs:
            template_id = kwargs["template_id"]
            del kwargs["template_id"]

            self.update_experiment_from_template(template_id, experiment_id)

        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)

        try:
            self.session.query(Experiment) \
                .filter_by(uuid=experiment_id) \
                .update(data)
            self.session.flush()
        except (InvalidRequestError, ProgrammingError) as e:
            raise BadRequest(str(e))

        self.fix_positions(project_id=experiment.project_id,
                           experiment_id=experiment.uuid,
                           new_position=experiment.position)

        return experiment

    def delete_experiment(self, project_id, experiment_id):
        """
        Delete an experiment in our database and in the object storage.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        dict
            The deletion result.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        experiment = self.session.query(Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        # remove comparisons
        self.session.query(Comparison).filter(Comparison.experiment_id == experiment_id).delete()

        # remove experiment operators
        self.session.query(Operator).filter(Operator.experiment_id == experiment_id).delete()

        # remove deployment (if exists) operators
        deployment = self.session.query(Deployment).filter(Deployment.experiment_id == experiment_id).first()
        if deployment:
            self.session.query(Operator).filter(Operator.deployment_id == deployment.uuid).delete()

        # remove deployments
        self.session.query(Deployment).filter(Deployment.experiment_id == experiment_id).delete()

        self.session.delete(experiment)
        self.session.flush()

        self.fix_positions(project_id=experiment.project_id)

        prefix = join("experiments", experiment_id)
        remove_objects(prefix=prefix)

        return {"message": "Experiment deleted"}

    def fix_positions(self, project_id, experiment_id=None, new_position=None):
        """
        Reorders the experiments in a project when an experiment is updated/deleted.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        new_position : int
            The position where the experiment is shown.
        """
        other_experiments = self.session.query(Experiment) \
            .filter_by(project_id=project_id) \
            .filter(Experiment.uuid != experiment_id) \
            .order_by(Experiment.position.asc()) \
            .all()

        if experiment_id is not None:
            experiment = self.session.query(Experiment).get(experiment_id)
            other_experiments.insert(new_position, experiment)

        for index, experiment in enumerate(other_experiments):
            data = {"position": index}
            is_last = (index == len(other_experiments) - 1)
            # if experiment_id WAS NOT informed, then set the higher position as is_active=True
            if experiment_id is None and is_last:
                data["is_active"] = True
            # if experiment_id WAS informed, then set experiment.is_active=True
            elif experiment_id is not None and experiment_id == experiment.uuid:
                data["is_active"] = True
            else:
                data["is_active"] = False

            self.session.query(Experiment) \
                .filter_by(uuid=experiment.uuid) \
                .update(data)

    def find_by_experiment_id(self, experiment_id):
        """
        Search the experiment by id.

        Parameters
        ----------
        experiment_id : str

        Returns
        -------
        dict
            The experiment attributes.

        Raises
        ------
        NotFound
            When experiment_id does not exist.
        """
        experiment = self.session.query(Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        return experiment

    def update_experiment_from_template(self, template_id, experiment_id):
        """
        Recreates the operators of experiment using a template.

        Parameters
        ----------
        template_id : str
        experiment_id : str
        """
        template = self.session.query(Template).get(template_id)

        if template is None:
            raise BadRequest("The specified template does not exist")

        # remove operators
        self.session.query(Operator).filter(Operator.experiment_id == experiment_id).delete()

        # save the operators created to get the created_uuid to use on dependencies
        operators_created = []
        for task in template.tasks:
            dependencies = []
            task_dependencies = task["dependencies"]
            if len(task_dependencies) > 0:
                for d in task_dependencies:
                    op_created = next((o for o in operators_created if o["uuid"] == d), None)
                    dependencies.append(op_created["created_uuid"])

            operator_id = uuid_alpha()
            objects = [
                Operator(
                    uuid=operator_id,
                    experiment_id=experiment_id,
                    task_id=task["task_id"],
                    dependencies=dependencies,
                    position_x=task["position_x"],
                    position_y=task["position_y"],
                )
            ]
            self.session.bulk_save_objects(objects)
            task["created_uuid"] = operator_id
            operators_created.append(task)
