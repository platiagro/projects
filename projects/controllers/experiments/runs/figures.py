# -*- coding: utf-8 -*-
"""Experiments Figures controller."""
import platiagro


class FigureController:
    def __init__(self, session):
        self.session = session

    def list_figures(self, project_id: str, experiment_id: str, run_id: str, operator_id: str):
        """
        Lists all figures from object storage as data URI scheme.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str
            The run_id. If `run_id=latest`, then returns figures from the latest run_id.
        operator_id : str

        Returns
        -------
        list
            A list of data URIs.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, run_id, or operator_id does not exist.
        """
        figures = platiagro.list_figures(experiment_id=experiment_id,
                                         operator_id=operator_id,
                                         run_id=run_id)
        return figures
