# -*- coding: utf-8 -*-
"""Experiments Runs controller."""
from kfp_server_api.rest import ApiException

from projects import kfp, models, schemas
from projects.exceptions import NotFound

NOT_FOUND = NotFound("The specified run does not exist")


class RunController:
    def __init__(self, session, kubeflow_userid=None):
        self.session = session
        self.kubeflow_userid = kubeflow_userid

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
            kfp.get_run(experiment_id=experiment_id,
                        run_id=run_id,
                        namespace=self.kubeflow_userid)
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
        runs = kfp.list_runs(experiment_id=experiment_id)
        return schemas.RunList.from_orm(runs, len(runs))

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
            raise NotFound("The specified experiment does not exist")

        run = kfp.run_experiment(experiment=experiment)

        run = kfp.get_run(experiment_id=experiment_id,
                          run_id=run.run_id,
                          namespace=self.kubeflow_userid)

        update_data = {"status": "Pending", "status_message": None}
        self.session.query(models.Operator) \
            .filter_by(experiment_id=experiment_id) \
            .update(update_data)
        self.session.commit()

        return schemas.Run.from_orm(run)

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
            run = kfp.get_run(experiment_id=experiment_id,
                              run_id=run_id,
                              namespace=self.kubeflow_userid)
        except (ApiException, ValueError):
            raise NOT_FOUND

        return schemas.Run.from_orm(run)

    def terminate_run(self, experiment_id: str, run_id: str):
        """
        Terminates a run in Kubeflow Pipelines.

        Parameters
        ----------
        experiment_id : str
        run_id : str

        Returns
        -------
        dict
            The termination result.

        Raises
        ------
        NotFound
            When any of experiment_id or run_id does not exist.
        """
        try:
            # Prevents a bug: if a run was deleted before kfp creates
            # resources on the cluster, operators would be stuck in status 'Pending'
            update_data = {"status": "Terminated", "status_message": None}
            self.session.query(models.Operator) \
                .filter_by(experiment_id=experiment_id) \
                .filter(models.Operator.status.in_(["Running", "Pending"])) \
                .update(update_data, synchronize_session='fetch')
            self.session.commit()

            run = kfp.terminate_run(experiment_id=experiment_id,
                                    run_id=run_id,
                                    namespace=self.kubeflow_userid)

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
            run = kfp.retry_run(experiment_id=experiment_id,
                                run_id=run_id,
                                namespace=self.kubeflow_userid)
        except ApiException:
            raise NOT_FOUND

        return run
