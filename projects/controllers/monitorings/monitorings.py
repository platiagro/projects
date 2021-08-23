# -*- coding: utf-8 -*-
"""Monitorings controller."""
from sqlalchemy import event

from projects import kfp, models, schemas
from projects.controllers.deployments.runs.runs import RunController
from projects.controllers.tasks import TaskController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import NotFound


NOT_FOUND = NotFound("The specified monitoring does not exist")


class MonitoringController:
    def __init__(self, session):
        self.session = session
        self.run_controller = RunController(session)
        self.task_controller = TaskController(session)

    @event.listens_for(models.Monitoring, "after_delete")
    def after_delete(self, _mapper, _connection, target):
        """
        Starts a pipeline that deletes K8s resources associated with target monitoring.

        Parameters
        ----------
        _mapper : sqlalchemy.orm.Mapper
        connection : sqlalchemy.engine.Connection
        target : models.Monitoring
        """
        kfp.delete_monitoring(monitoring=target, namespace=kfp.KF_PIPELINES_NAMESPACE)

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
        exists = self.session.query(models.Monitoring.uuid) \
            .filter_by(uuid=monitoring_id) \
            .scalar() is not None

        if not exists:
            raise NotFound("The specified monitoring does not exist")

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
        monitorings = self.session.query(models.Monitoring) \
            .filter_by(deployment_id=deployment_id) \
            .order_by(models.Monitoring.created_at.asc()) \
            .all()

        return schemas.MonitoringList.from_orm(monitorings, len(monitorings))

    def create_monitoring(self, monitoring: schemas.MonitoringCreate, deployment_id: str):
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
        self.task_controller.raise_if_task_does_not_exist(monitoring.task_id)

        monitoring = models.Monitoring(
            uuid=uuid_alpha(),
            deployment_id=deployment_id,
            task_id=monitoring.task_id,
        )
        self.session.add(monitoring)
        self.session.commit()
        self.session.refresh(monitoring)

        # Deploy the new monitoring
        kfp.create_monitoring(monitoring=monitoring, namespace=kfp.KF_PIPELINES_NAMESPACE)

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
