# -*- coding: utf-8 -*-
"""Experiments Metrics controller."""
import platiagro


class MetricController:
    def __init__(self, session):
        self.session = session

    def list_metrics(
        self, experiment_id: str, run_id: str, operator_id: str
    ):
        """
        Lists all metrics from object storage.

        Parameters
        ----------
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
            return platiagro.list_metrics(
                experiment_id=experiment_id, operator_id=operator_id, run_id=run_id
            )
        except FileNotFoundError:
            return []
