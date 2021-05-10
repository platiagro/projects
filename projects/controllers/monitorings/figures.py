# -*- coding: utf-8 -*-
"""Monitorings Figures controller."""
import platiagro


class MonitoringFigureController:
    def __init__(self, session):
        self.session = session

    def list_figures(self, project_id: str, deployment_id: str, monitoring_id: str):
        """
        Lists all figures from object storage as data URI scheme.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        monitoring_id : str

        Returns
        -------
        list
            A list of data URIs.

        Raises
        ------
        NotFound
            When any of project_id, deployment_id, monitoring_id does not exist.
        """
        figures = platiagro.list_figures(deployment_id=deployment_id,
                                         monitoring_id=monitoring_id)

        return figures
