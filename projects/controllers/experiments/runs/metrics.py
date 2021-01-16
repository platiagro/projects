# -*- coding: utf-8 -*-
"""Experiments Metrics controller."""
import platiagro
from werkzeug.exceptions import NotFound

from projects.controllers.experiments import ExperimentController
from projects.controllers.projects import ProjectController


class MetricController:
    def __init__(self, session):
        self.session = session
        self.project_controller = ProjectController(session)
        self.experiment_controller = ExperimentController(session)

    def list_metrics(self, project_id, experiment_id, run_id, operator_id):
        """
        Lists all metrics from object storage.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str
            The run_id. If `run_id=latest`, then returns metrics from the latest run_id.
        operator_id : str

        Returns
        -------
        list
            A list of metrics.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, run_id, or operator_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        try:
            return platiagro.list_metrics(experiment_id=experiment_id,
                                          operator_id=operator_id,
                                          run_id=run_id)
        except FileNotFoundError as e:
            raise NotFound(str(e))
