# -*- coding: utf-8 -*-
"""Experiments Runs controller."""
from kfp_server_api.rest import ApiException
from werkzeug.exceptions import NotFound

from projects.controllers.experiments import ExperimentController
from projects.controllers.projects import ProjectController
from projects.kfp import runs as kfp_runs
from projects.models import Experiment

NOT_FOUND = NotFound("The specified run does not exist")


class RunController:
    def __init__(self, session):
        self.session = session
        self.project_controller = ProjectController(session)
        self.experiment_controller = ExperimentController(session)

    def list_runs(self, project_id, experiment_id):
        """
        Lists all runs from an experiment.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        list
            A list of all runs from an experiment.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        runs = kfp_runs.list_runs(experiment_id=experiment_id)
        return runs

    def create_run(self, project_id, experiment_id):
        """
        Starts a new run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        experiment_id : str

        Returns
        -------
        dict
            The run attributes.

        Raises
        ------
        NotFound
            When either project_id or experiment_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)

        experiment = self.session.query(Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        run = kfp_runs.start_run(project_id=project_id,
                                 experiment_id=experiment_id,
                                 operators=experiment.operators)
        run["experimentId"] = experiment_id
        return run

    def get_run(self, project_id, experiment_id, run_id):
        """
        Details a run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str

        Returns
        -------
        dict
            The run attributes.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        try:
            run = kfp_runs.get_run(experiment_id=experiment_id,
                                   run_id=run_id)
        except (ApiException, ValueError):
            raise NOT_FOUND

        return run

    def terminate_run(self, project_id, experiment_id, run_id):
        """
        Terminates a run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str

        Returns
        -------
        dict
            The termination result.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        try:
            run = kfp_runs.terminate_run(experiment_id=experiment_id,
                                         run_id=run_id)
        except ApiException:
            raise NOT_FOUND

        return run

    def retry_run(self, project_id, experiment_id, run_id):
        """
        Retry a run in Kubeflow Pipelines.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str

        Returns
        -------
        dict
            The retry result.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        try:
            run = kfp_runs.retry_run(experiment_id=experiment_id,
                                     run_id=run_id)
        except ApiException:
            raise NOT_FOUND

        return run
