# -*- coding: utf-8 -*-
"""Experiments Metrics controller."""
import platiagro

from projects.exceptions import NotFound


class MetricController:
    def __init__(self, session):
        self.session = session

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
        """
        try:
            return platiagro.list_metrics(experiment_id=experiment_id,
                                          operator_id=operator_id,
                                          run_id=run_id)
        except FileNotFoundError as e:
            raise NotFound(str(e))
