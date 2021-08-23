# -*- coding: utf-8 -*-
"""Deployments controller."""
import sys
from datetime import datetime

from sqlalchemy import event

from projects import kfp, models, schemas
from projects.controllers.deployments.runs import RunController
from projects.controllers.templates import TemplateController
from projects.controllers.utils import uuid_alpha
from projects.controllers.tasks import TaskController
from projects.exceptions import BadRequest, NotFound

NOT_FOUND = NotFound("The specified deployment does not exist")

# Distance on the X axis from the leftmost operator
DATASET_OPERATOR_DISTANCE = 300
FONTE_DE_DADOS = "Fonte de dados"


class DeploymentController:
    def __init__(self, session, kubeflow_userid=None):
        self.session = session
        self.run_controller = RunController(session)
        self.template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
        self.task_controller = TaskController(session)

    @event.listens_for(models.Deployment, "after_delete")
    def after_delete(self, _mapper, connection, target):
        """
        Starts a pipeline that deletes K8s resources associated with target deployment.

        Parameters
        ----------
        _mapper : sqlalchemy.orm.Mapper
        connection : sqlalchemy.engine.Connection
        target : models.Deployment
        """
        kfp.delete_deployment(deployment=target, namespace=kfp.KF_PIPELINES_NAMESPACE)

    def raise_if_deployment_does_not_exist(self, deployment_id: str):
        """
        Raises an exception if the specified deployment does not exist.

        Parameters
        ----------
        deployment_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Deployment.uuid) \
            .filter_by(uuid=deployment_id) \
            .scalar() is not None

        if not exists:
            raise NOT_FOUND

    def list_deployments(self, project_id: str):
        """
        Lists all deployments under a project.

        Parameters
        ----------
        project_id: str

        Returns
        -------
        projects.schemas.deployment.DeploymentList
        """
        deployments = self.session.query(models.Deployment) \
            .filter_by(project_id=project_id) \
            .order_by(models.Deployment.position.asc()) \
            .all()

        return schemas.DeploymentList.from_orm(deployments, len(deployments))

    def create_deployment(self, deployment: schemas.DeploymentCreate, project_id: str):
        """
        Creates new deployments in our database and adjusts the position of others.

        Parameters
        ----------
        deployment : DeploymentCreate
        project_id : str

        Returns
        -------
        projects.schemas.deployment.Deployment

        Raises
        ------
        BadRequest
            When the parameters are invalid.
        """
        # ^ is xor operator. it's equivalent to (a and not b) or (not a and b)
        # this is a xor for three input variables
        if not ((bool(deployment.experiments) ^ bool(deployment.template_id)) or
                (bool(deployment.template_id) ^ bool(deployment.copy_from))):
            raise BadRequest("either experiments, templateId or copyFrom is required")

        if deployment.template_id:
            deployments = self.create_deployment_from_template(
                template_id=deployment.template_id,
                project_id=project_id
            )

        if deployment.copy_from:
            if not isinstance(deployment.name, str):
                raise BadRequest("name is required to duplicate deployment")

            stored_deployment = self.session.query(models.Deployment) \
                .filter(models.Deployment.project_id == project_id) \
                .filter_by(name=deployment.name) \
                .first()
            if stored_deployment:
                raise BadRequest("a deployment with that name already exists")

            deployments = self.copy_deployment(
                deployment_id=deployment.copy_from,
                name=deployment.name,
                project_id=project_id
            )

        if deployment.experiments:
            deployments = self.create_deployments_from_experiments(
                experiments=deployment.experiments,
                project_id=project_id
            )

        self.session.flush()

        for deployment in deployments:
            if len(deployment.operators) == 0:
                raise BadRequest("Necessary at least one operator.")
            elif len(deployment.operators) == 1 and deployment.operators[0].task.category == "DATASETS":
                raise BadRequest("Necessary at least one operator that is not a data source.")

        for deployment in deployments:
            self.run_controller.deploy_run(deployment)
            self.session.refresh(deployment)

        self.session.commit()

        return schemas.DeploymentList.from_orm(deployments, len(deployments))

    def get_deployment(self, deployment_id: str):
        """
        Details a deployment from our database.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.deployment.Deployment

        Raises
        ------
        NotFound
            When deployment_id does not exist.
        """
        deployment = self.session.query(models.Deployment).get(deployment_id)
        if deployment is None:
            raise NOT_FOUND

        return schemas.Deployment.from_orm(deployment)

    def update_deployment(self, deployment: schemas.DeploymentUpdate, project_id: str, deployment_id: str):
        """
        Updates a deployment in our database and adjusts the position of others.

        Parameters
        ----------
        deployment : projects.schemas.deployment.DeploymentUpdate
        project_id : str
        deployment_id : str

        Returns
        -------
        projects.schemas.deployment.Deployment

        Raises
        ------
        NotFound
            When deployment_id does not exist.
        BadRequest
            When name is already the name of another deployment.
        """
        self.raise_if_deployment_does_not_exist(deployment_id)

        stored_deployment = self.session.query(models.deployment.Deployment) \
            .filter(models.deployment.Deployment.project_id == project_id) \
            .filter_by(name=deployment.name) \
            .first()
        if stored_deployment and stored_deployment.uuid != deployment_id:
            raise BadRequest("a deployment with that name already exists")

        update_data = deployment.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Deployment).filter_by(uuid=deployment_id).update(update_data)

        if deployment.position:
            self.fix_positions(project_id=project_id,
                               deployment_id=deployment_id,
                               new_position=deployment.position)

        self.session.commit()

        deployment = self.session.query(models.Deployment).get(deployment_id)

        return schemas.Deployment.from_orm(deployment)

    def delete_deployment(self, project_id: str, deployment_id: str):
        """
        Delete a deployment in our database and in the object storage.

        Parameters
        ----------
        project_id: str
        deployment_id : str

        Raises
        ------
        NotFound
            When deployment_id does not exist.

        Returns
        -------
        projects.schemas.message.Message
        """
        deployment = self.session.query(models.Deployment).get(deployment_id)

        if deployment is None:
            raise NOT_FOUND

        self.session.delete(deployment)

        self.fix_positions(project_id=project_id)

        self.session.commit()

        return schemas.Message(message="Deployment deleted")

    def create_deployments_from_experiments(self, experiments: list, project_id: str):
        """
        Create deployments from given experiments.

        Parameters
        ----------
        experiments : list
            List of experiments uuids to copy.
        project_id : str

        Returns
        -------
        list
            A list of projects.models.deployment.Deployment.

        Raises
        ------
        BadRequest
            When any of the experiments does not exist.
        """
        experiments_dict = {e.uuid: e for e in self.session.query(models.Experiment).filter_by(project_id=project_id)}

        for experiment_id in experiments:
            if experiment_id not in experiments_dict:
                raise BadRequest("some experiments do not exist")

        deployments = []

        for experiment_id in experiments:
            experiment = experiments_dict[experiment_id]
            deployment = models.Deployment(uuid=uuid_alpha(),
                                           experiment_id=experiment_id,
                                           name=experiment.name,
                                           project_id=project_id)
            self.session.add(deployment)
            self.session.flush()

            deployments.append(deployment)

            self.copy_operators(deployment_id=deployment.uuid,
                                stored_operators=experiment.operators)

            self.fix_positions(project_id=project_id,
                               deployment_id=deployment.uuid,
                               new_position=sys.maxsize)  # will add to end of list

        return deployments

    def create_deployment_from_template(self, template_id: str, project_id: str):
        """
        Creates the operators of deployment using a template.

        Parameters
        ----------
        template_id : str
        project_id : str

        Returns
        -------
        list
            A list of projects.models.deployment.Deployment.
        """
        template = self.template_controller.get_template(template_id)
        deployment = models.Deployment(uuid=uuid_alpha(),
                                       name=template.name,
                                       project_id=project_id)
        self.session.add(deployment)
        self.session.flush()

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
                    deployment_id=deployment.uuid,
                    task_id=task["task_id"],
                    dependencies=dependencies,
                    position_x=task["position_x"],
                    position_y=task["position_y"],
                    status="Setted up"
                )
            ]
            self.session.bulk_save_objects(objects)
            task["created_uuid"] = operator_id
            operators_created.append(task)

        return [deployment]

    def copy_deployment(self, deployment_id: str, name: str, project_id: str):
        """
        Makes a copy of a deployment in our database.

        Paramenters
        -----------
        deployment_id : str
        name : str
        project_id : str

        Returns
        -------
        list
            A list of projects.models.deployment.Deployment.

        Raises
        ------
        BadRequest
            When deployment_id does not exist.
        """
        stored_deployment = self.session.query(models.Deployment).get(deployment_id)

        if stored_deployment is None:
            raise BadRequest("source deployment does not exist")

        deployment = models.Deployment(uuid=uuid_alpha(),
                                       experiment_id=stored_deployment.experiment_id,
                                       name=name,
                                       project_id=project_id)

        self.session.add(deployment)
        self.session.flush()

        self.copy_operators(deployment_id=deployment.uuid,
                            stored_operators=stored_deployment.operators)

        self.fix_positions(project_id=project_id,
                           deployment_id=deployment.uuid,
                           new_position=sys.maxsize)  # will add to end of list

        return [deployment]

    # That will make independents operators depends on generated dataset
    def set_dependents_for_generated_dataset_operator(self,
                                                      copies_map,
                                                      generated_dataset_operator_uuid):
        """
        Checks operators without dependency and make them depends on generated dataset operator

        Parameters
        ----------
        copies_map : dict
        generated_dataset_operator_uuid: str
        """

        dependencies_as_tuple_list = list(copies_map.items())
        for tuple_element in dependencies_as_tuple_list:
            dependencies_dict = tuple_element[1]
            if not dependencies_dict.get('dependencies'):
                independent_operator_uuid = dependencies_dict.get('copy_uuid')
                update_data = {"dependencies": [generated_dataset_operator_uuid]}
                update_data.update({"updated_at": datetime.utcnow()})
                self.session.query(models.Operator).filter_by(uuid=independent_operator_uuid).update(update_data)

    def set_dependencies_on_new_operators(self, copies_map):
        """
        Sets dependency for new operators

        Parameters
        ----------
        copies_map : dict
        """
        for _, value in copies_map.items():
            if value.get('dependencies'):
                update_data = {"dependencies": [copies_map[d]["copy_uuid"] for d in value["dependencies"]]}
                update_data.update({"updated_at": datetime.utcnow()})
                self.session.query(models.Operator).filter_by(uuid=value["copy_uuid"]).update(update_data)

    def copy_operators(self, deployment_id: str, stored_operators: schemas.OperatorList):
        """
        Copies the operators to a deployment.
        Creates new uuids and don't keep the experiment_id/deployment_id relationship.

        Parameters
        ----------
        stored_operators : projects.schemas.operator.OperatorsList
        deployment_id : str
        """
        if len(stored_operators) == 0:
            raise BadRequest("Necessary at least one operator.")

        # Creates a dict to map source operator_id to its copy operator_id.
        # This map will be used to build the dependencies using new operator_ids
        copies_map = {}

        # just a simple flag to detect the existence of a dataset operator
        some_stored_operators_is_dataset = False

        # default position, in case we have to create a dataset operator
        leftmost_operator_position = (stored_operators[0].position_x, stored_operators[0].position_y)

        for stored_operator in stored_operators:

            # If we have to create a dataset operator, it is interesting that we put before the leftmost position
            if stored_operator.position_x < leftmost_operator_position[0]:
                leftmost_operator_position = (stored_operator.position_x, stored_operator.position_y)

            if stored_operator.task.category == "DATASETS":
                name = FONTE_DE_DADOS
                parameters = {"type": "L", "dataset": None}
                some_stored_operators_is_dataset = True
            else:
                name = None
                parameters = stored_operator.parameters

            operator_id = uuid_alpha()

            operator = models.Operator(uuid=operator_id,
                                       name=name,
                                       deployment_id=deployment_id,
                                       task_id=stored_operator.task_id,
                                       dependencies=[],
                                       status="Setted up",
                                       parameters=parameters,
                                       position_x=stored_operator.position_x,
                                       position_y=stored_operator.position_y)

            self.session.add(operator)
            self.session.flush()

            copies_map[stored_operator.uuid] = {
                "copy_uuid": operator_id,
                "dependencies": stored_operator.dependencies,
            }

        # creates a DATASET type operator if doesn't exist any
        if not some_stored_operators_is_dataset:
            generated_dataset_operator_uuid = uuid_alpha()
            operator = models.Operator(uuid=generated_dataset_operator_uuid,
                                       name=FONTE_DE_DADOS,
                                       deployment_id=deployment_id,
                                       task_id=self.task_controller.get_or_create_dataset_task_if_not_exist(),
                                       dependencies=[],
                                       parameters={"type": "L", "dataset": None},
                                       position_x=leftmost_operator_position[0] - DATASET_OPERATOR_DISTANCE,
                                       position_y=leftmost_operator_position[1])

            self.session.add(operator)
            self.session.flush()
            self.set_dependents_for_generated_dataset_operator(copies_map, generated_dataset_operator_uuid)

        self.set_dependencies_on_new_operators(copies_map)

    def fix_positions(self, project_id: str, deployment_id=None, new_position=None):
        """
        Reorders the deployments in a project when a deployment is updated/deleted.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        new_position : int
            The position where the experiment is shown.
        """
        other_deployments = self.session.query(models.Deployment) \
            .filter_by(project_id=project_id) \
            .filter(models.Deployment.uuid != deployment_id) \
            .order_by(models.Deployment.position.asc()) \
            .all()

        if deployment_id is not None:
            deployment = self.session.query(models.Deployment).get(deployment_id)
            other_deployments.insert(new_position, deployment)

        for index, deployment in enumerate(other_deployments):
            data = {"position": index}
            is_last = (index == len(other_deployments) - 1)
            # if deployment_id WAS NOT informed, then set the higher position as is_active=True
            if deployment_id is None and is_last:
                data["is_active"] = True
            # if deployment_id WAS informed, then set experiment.is_active=True
            elif deployment_id is not None and deployment_id == deployment.uuid:
                data["is_active"] = True
            else:
                data["is_active"] = False

            self.session.query(models.Deployment).filter_by(uuid=deployment.uuid).update(data)
