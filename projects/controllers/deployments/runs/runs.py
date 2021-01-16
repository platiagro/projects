# -*- coding: utf-8 -*-
"""Deployments Runs controller."""
from kubernetes import client
from werkzeug.exceptions import BadRequest, NotFound

from projects.models import Deployment
from projects.kfp import KF_PIPELINES_NAMESPACE, kfp_client
from projects.kfp import runs as kfp_runs
from projects.kfp.pipeline import undeploy_pipeline
from projects.kfp.deployments import get_deployment_runs

from projects.kubernetes.kube_config import load_kube_config


NOT_FOUND = NotFound("The specified deployment does not exist")


class RunController:
    def __init__(self, session):
        self.session = session

    def list_runs(self, project_id, deployment_id):
        """
        Lists all runs under a deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str

        Returns
        -------
        list
            A list of all runs from a deployment.

        Raises
        ------
        NotFound
            When either project_id or deployment_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        runs = get_deployment_runs(deployment_id)

        return [runs]

    def create_run(self, project_id, deployment_id):
        """
        Starts a new run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        deployment_id : str

        Returns
        -------
        dict
            The run attributes.

        Raises
        ------
        NotFound
            When any of project_id, or deployment_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)

        deployment = self.session.query(Deployment).get(self.session, deployment_id)

        if deployment is None:
            raise NOT_FOUND

        # Removes operators that don't have a deployment_notebook (eg. Upload de Dados).
        # Then, fix dependencies in their children.
        operators = self.remove_non_deployable_operators(deployment.operators)

        try:
            run = kfp_runs.start_run(operators=operators,
                                     project_id=deployment.project_id,
                                     experiment_id=deployment.experiment_id,
                                     deployment_id=deployment_id,
                                     deployment_name=deployment.name)
        except ValueError as e:
            raise BadRequest(str(e))

        run["deploymentId"] = deployment_id
        return run

    def get_run(self, project_id, deployment_id, run_id):
        """
        Details a run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        run_id : str

        Returns
        -------
        dict
            The run attributes.

        Raises
        ------
        NotFound
            When any of project_id, deployment_id, or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        run = get_deployment_runs(deployment_id)

        return run

    def terminate_run(self, project_id, deployment_id, run_id):
        """
        Terminates a run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        run_id : str

        Returns
        -------
        dict
            The termination result.

        Raises
        ------
        NotFound
            When any of project_id, deployment_id, or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.deployment_controller.raise_if_deployment_does_not_exist(deployment_id)

        load_kube_config()
        api = client.CustomObjectsApi()
        custom_objects = api.list_namespaced_custom_object(
            "machinelearning.seldon.io",
            "v1alpha2",
            KF_PIPELINES_NAMESPACE,
            "seldondeployments"
        )
        deployments_objects = custom_objects["items"]

        if deployments_objects:
            for deployment in deployments_objects:
                if deployment["metadata"]["name"] == deployment_id:
                    undeploy_pipeline(deployment)

        deployment_run = get_deployment_runs(deployment_id)

        if not deployment_run:
            raise NotFound("Deployment run does not exist.")

        kfp_client().runs.delete_run(deployment_run["runId"])

        return {"message": "Deployment deleted."}

    def remove_non_deployable_operators(self, operators):
        """
        Removes operators that are not part of the deployment pipeline.

        Parameters
        ----------
        operators : list
            Original pipeline operators.

        Returns
        -------
        list
            A list of all deployable operators.

        Notes
        -----
        If the non-deployable operator is dependent on another operator, it will be
        removed from that operator's dependency list.
        """
        deployable_operators = [o for o in operators if o.task.deployment_notebook_path is not None]
        non_deployable_operators = self.get_non_deployable_operators(operators, deployable_operators)

        for operator in deployable_operators:
            dependencies = set(operator.dependencies)
            operator.dependencies = list(dependencies - set(non_deployable_operators))

        return deployable_operators

    def get_non_deployable_operators(self, operators, deployable_operators):
        """
        Get all non-deployable operators from a deployment run.

        Parameters
        ----------
        operators : list
        deployable_operators : list

        Returns
        -------
        list
            A list of non deployable operators.
        """
        non_deployable_operators = []
        for operator in operators:
            if operator.task.deployment_notebook_path is None:
                # checks if the non-deployable operator has dependency
                if operator.dependencies:
                    dependency = operator.dependencies

                    # looks for who has the non-deployable operator as dependency
                    # and assign the dependency of the non-deployable operator to this operator
                    for op in deployable_operators:
                        if operator.uuid in op.dependencies:
                            op.dependencies = dependency

                non_deployable_operators.append(operator.uuid)

        return non_deployable_operators
