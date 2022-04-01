# -*- coding: utf-8 -*-
"""Monitorings controller."""
import warnings

from sqlalchemy import event

from projects import models, schemas
from projects.controllers.deployments.runs.runs import RunController
from projects.controllers.tasks import TaskController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, NotFound
from projects.kfp.monitorings import deploy_monitoring, undeploy_monitoring

NOT_FOUND = NotFound(
    code="MonitoringNotFound", message="The specified monitoring does not exist"
)


class MonitoringController:
    def __init__(self, session, background_tasks=None):
        self.session = session
        self.background_tasks = background_tasks
        self.run_controller = RunController(session)
        self.task_controller = TaskController(session)

    @staticmethod
    @event.listens_for(models.Monitoring, "after_delete")
    def after_delete(_mapper, _connection, target):
        """
        Starts a pipeline that deletes K8s resources associated with target monitoring.
        Parameters
        ----------
        _mapper : sqlalchemy.orm.Mapper
        connection : sqlalchemy.engine.Connection
        target : models.Monitoring
        """
        try:
            undeploy_monitoring(monitoring_id=target.uuid)
        except NotFound as e:
            warnings.warn(e.message)

    def raise_if_monitoring_does_not_exist(self, monitoring_id: str):
        """
        Raises an exception if the specified monitoring does not exist.

        Parameters
        ----------
        monitoring_id : str

        Raises
        ------
        NotFound
        """
        exists = (
            self.session.query(models.Monitoring.uuid)
            .filter_by(uuid=monitoring_id)
            .scalar()
            is not None
        )

        if not exists:
            raise NotFound(
                code="MonitoringNotFound",
                message="The specified monitoring does not exist",
            )

    def list_monitorings(self, deployment_id: str):
        """
        Lists all monitorings under a deployment.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.monitoring.MonitoringList
        """
        monitorings = (
            self.session.query(models.Monitoring)
            .filter_by(deployment_id=deployment_id)
            .order_by(models.Monitoring.created_at.asc())
            .all()
        )

        return schemas.MonitoringList.from_orm(monitorings, len(monitorings))

    def create_monitoring(
        self, monitoring: schemas.MonitoringCreate, deployment_id: str
    ):
        """
        Creates a new monitoring in our database.

        Parameters
        ----------
        monitoring : projects.schemas.monitoring.MonitoringCreate
        project_id : str
        deployment_id : str

        Returns
        -------
        projects.schemas.monitoring.Monitoring
        """
        task_exists = (
            self.session.query(models.Task.uuid)
            .filter_by(uuid=monitoring.task_id)
            .scalar()
            is not None
        )

        if not task_exists:
            raise BadRequest(
                code="InvalidTaskId",
                message="The specified task does not exist",
            )

        monitoring = models.Monitoring(
            uuid=uuid_alpha(),
            deployment_id=deployment_id,
            task_id=monitoring.task_id,
        )
        self.session.add(monitoring)
        self.session.commit()
        self.session.refresh(monitoring)

        deployment = self.session.query(models.Deployment).get(deployment_id)
        run = self.run_controller.get_run(deployment_id)

        # Uses empty run_id if a deployment does not have a run
        if not run:
            run = {"runId": ""}

        # Deploy the new monitoring
        self.background_tasks.add_task(
            deploy_monitoring,
            deployment_id=deployment_id,
            experiment_id=deployment.experiment_id,
            run_id=run["runId"],
            task_id=monitoring.task_id,
            monitoring_id=monitoring.uuid,
        )

        return schemas.Monitoring.from_orm(monitoring)

    def delete_monitoring(self, uuid):
        """
        Delete a monitoring in our database.

        Parameters
        ----------
        uuid : str

        Returns
        -------
        projects.schemas.message.Message
        """
        monitoring = self.session.query(models.Monitoring).get(uuid)

        if monitoring is None:
            raise NOT_FOUND

        self.session.delete(monitoring)
        self.session.commit()

        return schemas.Message(message="Monitoring deleted")
