# -*- coding: utf-8 -*-
"""Experiments Runs controller."""
from kfp_server_api.rest import ApiException

from projects import models, schemas
from projects.exceptions import NotFound
from projects.kfp import runs as kfp_runs

NOT_FOUND = NotFound("The specified run does not exist")


class RunController:
    def __init__(self, session):
        self.session = session

    def raise_if_run_does_not_exist(self, run_id: str, experiment_id: str):
        """
        Raises an exception if the specified run does not exist.

        Parameters
        ----------
        run_id : str
        experiment_id : str

        Raises
        ------
        NotFound
        """
        try:
            kfp_runs.get_run(experiment_id=experiment_id,
                             run_id=run_id)
        except (ApiException, ValueError):
            raise NOT_FOUND

    def list_runs(self, project_id: str, experiment_id: str):
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
            When experiment_id does not exist.
        """
        runs = kfp_runs.list_runs(experiment_id=experiment_id)
        return schemas.RunList.from_model(runs, len(runs))

    def create_run(self, project_id: str, experiment_id: str):
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
            When experiment_id does not exist.
        """
        experiment = self.session.query(models.Experiment).get(experiment_id)

        if experiment is None:
            raise NOT_FOUND

        run = kfp_runs.start_run(project_id=project_id,
                                 experiment_id=experiment_id,
                                 operators=experiment.operators)
        run["experimentId"] = experiment_id

        update_data = {"status": "Pending"}
        self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .update(update_data)
        self.session.commit()

        return schemas.Run.from_model(run)

    def get_run(self, project_id: str, experiment_id: str, run_id: str):
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
        try:
            run = kfp_runs.get_run(experiment_id=experiment_id,
                                   run_id=run_id)
        except (ApiException, ValueError):
            raise NOT_FOUND

        return schemas.Run.from_model(run)

    def terminate_run(self, project_id: str, experiment_id: str, run_id: str):
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
        try:
            run = kfp_runs.terminate_run(experiment_id=experiment_id,
                                         run_id=run_id)
        except ApiException:
            raise NOT_FOUND

        return run

    def retry_run(self, project_id: str, experiment_id: str, run_id: str):
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
        try:
            run = kfp_runs.retry_run(experiment_id=experiment_id,
                                     run_id=run_id)
        except ApiException:
            raise NOT_FOUND

        return run
