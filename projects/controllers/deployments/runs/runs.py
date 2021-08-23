# -*- coding: utf-8 -*-
"""Deployments Runs controller."""
from kubernetes.client.rest import ApiException

from projects import kfp, models, schemas
from projects.exceptions import NotFound
from projects.kubernetes.seldon import get_seldon_deployment_url

NOT_FOUND = NotFound("The specified run does not exist")


class RunController:
    def __init__(self, session):
        self.session = session

    def raise_if_run_does_not_exist(self, run_id: str, deployment_id: str):
        """
        Raises an exception if the specified run does not exist.

        Parameters
        ----------
        run_id : str
        deployment_id : str

        Raises
        ------
        NotFound
        """
        try:
            kfp.get_run(deployment_id=deployment_id,
                        run_id=run_id)
        except (ApiException, ValueError):
            raise NOT_FOUND

    def list_runs(self, deployment_id: str):
        """
        Lists all runs under a deployment.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.run.RunList
        """
        runs = kfp.list_runs(deployment_id=deployment_id)
        return schemas.RunList.from_orm(runs, len(runs))

    def create_run(self, deployment_id: str):
        """
        Update deployment url.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.run.Run

        Raises
        ------
        NotFound
            When any of project_id, or deployment_id does not exist.
        """
        deployment = self.session.query(models.Deployment).get(deployment_id)

        url = get_seldon_deployment_url(deployment_id)

        self.session.query(models.Deployment) \
            .filter_by(uuid=deployment_id) \
            .update({"url": url})
        self.session.commit()

        run = self.get_run(deployment_id)

        # Uses empty run if a deployment does not have a run
        if not run:
            operators = dict((o.uuid, {"taskId": o.task.uuid, "parameters": {}}) for o in deployment.operators)
            run = {
                "uuid": "",
                "operators": operators,
                "createdAt": deployment.created_at,
            }

        run["deploymentId"] = deployment_id

        return run

    def deploy_run(self, deployment):
        """
        Starts a new run in Kubeflow Pipelines.

        Parameters
        ----------
        deployment : projects.models.deployment.Deployment

        Returns
        -------
        projects.schemas.run.Run

        Raises
        ------
        NotFound
            When any of project_id, or deployment_id does not exist.
        """
        if deployment is None:
            raise NotFound("The specified deployment does not exist")

        run = kfp.run_deployment(deployment=deployment, namespace=kfp.KF_PIPELINES_NAMESPACE)

        run = kfp.get_run(deployment_id=deployment.uuid,
                          run_id=run.run_id)

        return schemas.Run.from_orm(run)

    def get_run(self, deployment_id: str):
        """
        Details a run in Kubeflow Pipelines.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.run.Run

        Raises
        ------
        NotFound
            When any of deployment_id, or run_id does not exist.
        """
        try:
            run = kfp.get_run(deployment_id=deployment_id,
                              run_id="latest")
        except (ApiException, ValueError):
            raise NOT_FOUND

        return schemas.Run.from_orm(run)

    def terminate_run(self, deployment_id):
        """
        Terminates a run in Kubeflow Pipelines.

        Parameters
        ----------
        deployment_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When deployment run does not exist.
        """
        deployment = self.session.query(models.Deployment) \
            .get(deployment_id)

        kfp.delete_deployment(deployment=deployment, namespace=kfp.KF_PIPELINES_NAMESPACE)

        return schemas.Message(message="Deployment deleted")
