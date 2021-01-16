# -*- coding: utf-8 -*-
"""Experiments Logs controller."""
from json import loads

from projects.controllers.experiments import ExperimentController
from projects.controllers.operators import OperatorController
from projects.controllers.projects import ProjectController
from projects.controllers.utils import raise_if_run_does_not_exist

from projects.jupyter import get_notebook_logs

from projects.kfp import kfp_client
from projects.kfp.runs import get_latest_run_id
from projects.kubernetes.utils import search_for_pod_info


class LogController:
    def __init__(self, session):
        self.session = session
        self.project_controller = ProjectController(session)
        self.experiment_controller = ExperimentController(session)
        self.operator_controller = OperatorController(session)

    def get_logs(self, project_id, experiment_id, run_id, operator_id):
        """
        Get logs from a experiment run.

        Parameters
        ----------
        project_id : str
        experiment_id : str
        run_id : str
            The run_id. If `run_id=latest`, then returns logs from the latest run_id.
        operator_id : str

        Returns
        -------
        dict
            A dict of logs from a run.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, operator_id or run_id does not exist.
        """
        self.project_controller.raise_if_project_does_not_exist(project_id)
        self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)
        self.operator_controller.raise_if_operator_does_not_exist(operator_id)

        logs = get_notebook_logs(experiment_id=experiment_id,
                                 operator_id=operator_id)

        if not logs:
            # No notebooks or logs were found in the Jupyter API.
            # Search for logs in the operator pod details.

            if run_id == "latest":
                run_id = get_latest_run_id(experiment_id)

            raise_if_run_does_not_exist(run_id)

            run_details = kfp_client().get_run(run_id=run_id)
            details = loads(run_details.pipeline_runtime.workflow_manifest)
            operator = search_for_pod_info(details, operator_id)

            if operator and operator["status"] == "Failed":
                logs = {"exception": operator["message"],
                        "traceback": [f"Kernel has died: {operator['message']}"]}
            else:
                logs = {"message": "Notebook finished with status completed."}

        return logs
