# -*- coding: utf-8 -*-
"""Experiments controller."""
import sys
from datetime import datetime
from typing import Optional

from projects import models, schemas
from projects.controllers.operators import OperatorController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, NotFound


NOT_FOUND = NotFound("The specified experiment does not exist")


class ExperimentController:
    def __init__(self, session):
        self.session = session
        self.operator_controller = OperatorController(session)

    def raise_if_experiment_does_not_exist(self, experiment_id: str):
        """
        Raises an exception if the specified experiment does not exist.

        Parameters
        ----------
        experiment_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Experiment.uuid) \
            .filter_by(uuid=experiment_id) \
            .scalar() is not None

        if not exists:
            raise NotFound("The specified experiment does not exist")

    def list_experiments(self, project_id: str):
        """
        Lists all experiments under a project.

        Parameters
        ----------
        project_id: str

        Returns
        -------
        projects.schemas.experiment.ExperimentList

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        experiments = self.session.query(models.Experiment) \
            .filter_by(project_id=project_id) \
            .order_by(models.Experiment.position.asc()) \
            .all()

        return schemas.ExperimentList.from_model(experiments, len(experiments))

    def create_experiment(self, experiment: schemas.ExperimentCreate, project_id: str):
        """
        Creates a new experiment in our database and adjusts the position of others.
        The new experiment is added to the end of the experiment list.

        Parameters
        ----------
        experiment: projects.schemas.experiment.ExperimentCreate
        project_id : str

        Returns
        -------
        projects.schemas.experiment.Experiment

        Raises
        ------
        NotFound
            When project_id does not exist.
        BadRequest
            When name is not a str instance.
            When name is already the name of another experiment.
        """
        if not isinstance(experiment.name, str):
            raise BadRequest("name is required")

        stored_experiment = self.session.query(models.Experiment) \
            .filter(models.Experiment.project_id == project_id) \
            .filter_by(name=experiment.name) \
            .first()
        if stored_experiment:
            raise BadRequest("an experiment with that name already exists")

        if experiment.copy_from:
            experiment = self.copy_experiment(experiment=experiment, project_id=project_id)
        else:
            experiment = models.Experiment(uuid=uuid_alpha(), name=experiment.name, project_id=project_id)
            self.session.add(experiment)
            self.session.flush()

        self.fix_positions(project_id=project_id,
                           experiment_id=experiment.uuid,
                           new_position=sys.maxsize)  # will add to end of list

        self.session.commit()
        self.session.refresh(experiment)

        return schemas.Experiment.from_model(experiment)

    def get_experiment(self, project_id: str, experiment_id: str):
        """
        Details an experiment from our database.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        projects.schemas.experiment.Experiment

        Raises
        ------
        NotFound
            When experiment_id does not exist.
        """
        experiment = self.session.query(models.Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        return schemas.Experiment.from_model(experiment)

    def update_experiment(self, experiment: schemas.ExperimentUpdate, project_id: str, experiment_id: str):
        """
        Updates an experiment in our database and adjusts the position of others.

        Parameters
        ----------
        experiment: projects.schemas.experiment.ExperimentUpdate
        project_id : str
        experiment_id : str

        Returns
        -------
        projects.schemas.experiment.Experiment

        Raises
        ------
        NotFound
            When experiment_id does not exist.
        BadRequest
            When name is already the name of another experiment.
            When `experiment.template_id` is informed but it does not exist.
        """
        self.raise_if_experiment_does_not_exist(experiment_id)

        stored_experiment = self.session.query(models.Experiment) \
            .filter(models.Experiment.project_id == project_id) \
            .filter_by(name=experiment.name) \
            .first()
        if stored_experiment and stored_experiment.uuid != experiment_id:
            raise BadRequest("an experiment with that name already exists")

        if experiment.template_id:
            return self.update_experiment_from_template(experiment=experiment, experiment_id=experiment_id)

        update_data = experiment.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Experiment).filter_by(uuid=experiment_id).update(update_data)

        if experiment.position:
            self.fix_positions(project_id=project_id,
                               experiment_id=experiment_id,
                               new_position=experiment.position)

        self.session.commit()

        experiment = self.session.query(models.Experiment).get(experiment_id)

        return schemas.Experiment.from_model(experiment)

    def delete_experiment(self, project_id, experiment_id):
        """
        Delete an experiment in our database and in the object storage.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When experiment_id does not exist.
        """
        experiment = self.session.query(models.Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        # remove comparisons
        self.session.query(models.Comparison) \
            .filter(models.Comparison.experiment_id == experiment_id) \
            .delete()

        # remove experiment operators
        self.session.query(models.Operator) \
            .filter(models.Operator.experiment_id == experiment_id) \
            .delete()

        # update deployments experiment id to None
        self.session.query(models.Deployment) \
            .filter(models.Deployment.experiment_id == experiment_id) \
            .update({"experiment_id": None})

        self.session.delete(experiment)
        self.session.flush()

        self.fix_positions(project_id=project_id)
        self.session.commit()

        return schemas.Message(message="Experiment deleted")

    def copy_experiment(self, experiment: schemas.ExperimentCreate, project_id: str):
        """
        Makes a copy of an experiment in our database.

        Parameters
        ----------
        task: projects.schemas.experiment.ExperimentCreate
        project_id: str

        Returns
        -------
        projects.schemas.experiment.Experiment

        Raises
        ------
        BadRequest
            When copy_from does not exist.
        """
        stored_experiment = self.session.query(models.Experiment).get(experiment.copy_from)

        if stored_experiment is None:
            raise BadRequest("source experiment does not exist")

        experiment = models.Experiment(uuid=uuid_alpha(), name=experiment.name, project_id=project_id)
        self.session.add(experiment)
        self.session.flush()

        # Creates a dict to map source operator_id to its copy operator_id.
        # This map will be used to build the dependencies using new operator_ids
        copies_map = {}

        for stored_operator in stored_experiment.operators:
            operator = schemas.OperatorCreate(
                task_id=stored_operator.task_id,
                experiment_id=experiment.uuid,
                parameters=stored_operator.parameters,
                position_x=stored_operator.position_x,
                position_y=stored_operator.position_y,
            )
            operator = self.operator_controller.create_operator(operator=operator, project_id=project_id, experiment_id=experiment.uuid)

            copies_map[stored_operator.uuid] = {
                "copy_uuid": operator.uuid,
                "dependencies": stored_operator.dependencies,
            }

        # sets dependencies on new operators
        for _, value in copies_map.items():
            operator = schemas.OperatorUpdate(
                dependencies=[copies_map[d]["copy_uuid"] for d in value["dependencies"]],
            )
            self.operator_controller.update_operator(project_id=project_id,
                                                     experiment_id=experiment.uuid,
                                                     operator_id=value["copy_uuid"],
                                                     operator=operator)

        return experiment

    def update_experiment_from_template(self, experiment: schemas.ExperimentUpdate, experiment_id: str):
        """
        Recreates the operators of experiment using a template.

        Parameters
        ----------
        experiment : projects.schemas.experiment.ExperimentUpdate
        experiment_id : str
        """
        template = self.session.query(models.Template).get(experiment.template_id)

        if template is None:
            raise BadRequest("The specified template does not exist")

        # remove operators
        self.session.query(models.Operator) \
            .filter(models.Operator.experiment_id == experiment_id) \
            .delete()

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
                models.Operator(
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

    def fix_positions(self, project_id: str, experiment_id: Optional[str] = None, new_position: Optional[int] = None):
        """
        Reorders the experiments in a project when an experiment is updated/deleted.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        new_position : int
            The position where the experiment is shown.
        """
        other_experiments = self.session.query(models.Experiment) \
            .filter_by(project_id=project_id) \
            .filter(models.Experiment.uuid != experiment_id) \
            .order_by(models.Experiment.position.asc()) \
            .all()

        if experiment_id is not None:
            experiment = self.session.query(models.Experiment).get(experiment_id)
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

            self.session.query(models.Experiment) \
                .filter_by(uuid=experiment.uuid) \
                .update(data)
