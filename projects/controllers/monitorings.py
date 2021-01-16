# -*- coding: utf-8 -*-
"""Monitorings controller."""
from werkzeug.exceptions import NotFound

from projects.controllers.deployments import DeploymentController
from projects.controllers.projects import ProjectController
from projects.controllers.tasks import TaskController
from projects.controllers.utils import uuid_alpha
from projects.models import Monitoring


NOT_FOUND = NotFound("The specified monitoring does not exist")


class MonitoringController:
    def __init__(self, session):
        self.session = session
        self.project_controller = ProjectController(session)
        self.deployment_controller = DeploymentController(session)
        self.task_controller = TaskController(session)

    def list_monitorings(self, project_id, deployment_id):
        """
        Lists all monitorings under a deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str

        Returns
        -------
        list
            A list of all monitorings.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        monitorings = self.session.query(Monitoring) \
            .filter_by(deployment_id=deployment_id) \
            .order_by(Monitoring.created_at.asc()) \
            .all()

        return monitorings

    def create_monitoring(self, project_id,
                          deployment_id=None,
                          task_id=None):
        """
        Creates a new monitoring in our database.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        task_id : str

        Returns
        -------
        dict
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)
        self.task_controller.raise_if_task_does_not_exist(task_id)

        monitoring = Monitoring(
            uuid=uuid_alpha(),
            deployment_id=deployment_id,
            task_id=task_id
        )
        self.session.add(monitoring)
        return monitoring

    def delete_monitoring(self, uuid, project_id, deployment_id):
        """
        Delete a monitoring in our database.

        Parameters
        ----------
        uuid : str
        project_id : str
        deployment_id : str

        Returns
        -------
        dict
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        monitoring = self.session.query(Monitoring).get(uuid)

        if monitoring is None:
            raise NOT_FOUND

        self.session.delete(monitoring)

        return {"message": "Monitoring deleted"}
