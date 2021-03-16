# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
import re
from typing import List

from io import StringIO

from projects.exceptions import NotFound
from projects.kfp.runs import get_latest_run_id
from projects.kubernetes.argo import list_workflow_pods
from projects.kubernetes.seldon import list_deployment_pods
from projects.kubernetes.utils import get_container_logs


EXCLUDE_CONTAINERS = ["istio-proxy", "wait", "seldon-container-engine"]
TIME_STAMP_PATTERN = r'\d{4}-\d{2}-\d{2}(:?\s|T)\d{2}:\d{2}:\d{2}(:?.|,)\d+Z?\s?'
LOG_MESSAGE_PATTERN = r'[a-zA-Z0-9\u00C0-\u00D6\u00D8-\u00f6\u00f8-\u00ff\"\'.\-@_,!#$%^&*()\[\]<>?\/|}{~:]{1,}'
LOG_LEVEL_PATTERN = r'(?<![\\w\\d])INFO(?![\\w\\d])|(?<![\\w\\d])WARNING(?![\\w\\d])|(?<![\\w\\d])WARN(?![\\w\\d])|(?<![\\w\\d])ERROR(?![\\w\\d])'

NOT_FOUND = NotFound("The specified run does not exist")


class LogController:
    def __init__(self, session):
        self.session = session

    def list_logs(self, project_id: str, deployment_id: str, run_id: str):
        """
        Lists logs from a deployment.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        run_id : str

        Returns
        -------
        list
            A list of all logs from a run.
        """
        # Tries to retrieve any pods associated to a seldondeployment
        pods = list_deployment_pods(deployment_id=deployment_id)

        if len(pods) == 0:
            # When there aren't any seldondeployments, retrieves the workflow pods.
            # This is useful for debugging failures during the workflow execution.
            if run_id == "latest":
                run_id = get_latest_run_id(deployment_id)

            pods = list_workflow_pods(run_id=run_id)

        logs = self.pods_to_logs(pods)

        return logs

    def pods_to_logs(self, pods: List):
        """
        Transform raw log text into human-readable logs.

        Parameters
        ----------
        pods : list
            A list of pod details.

        Returns
        -------
        list
            Detailed logs with level, Time Stamp and message from pod container.
        """
        logs = []
        for pod in pods:
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS:
                    logs_text = get_container_logs(pod, container)
                    status = "Completed" if logs_text is not None else "Creating"

                    if container.env is None:
                        task_name = pod.metadata.name
                    else:
                        task_name = next((e.value for e in container.env if e.name == "TASK_NAME"), pod.metadata.name)

                    operator_info = {
                        "status": status,
                        "containerName": task_name,
                        "logs": self.parse_logs(logs_text),
                    }
                    logs.append(operator_info)

        return logs

    def parse_logs(self, raw_log):
        """
        Transform raw log text into human-readable logs.

        Parameters
        ----------
        raw_log : str
            The raw log content.

        Returns
        -------
        dict
            Detailed logs with level, Time Stamp and message from pod container.
        """
        logs = []
        buf = StringIO(raw_log)
        line = buf.readline()

        while line:
            line = line.replace("\n", "")

            timestamp = re.search(TIME_STAMP_PATTERN, line).group()
            line = re.sub(timestamp, "", line)

            level = re.findall(LOG_LEVEL_PATTERN, line)
            level = " ".join([str(x) for x in level])
            line = line.replace(level, "")

            line = re.sub(r"( [-:*]{1})", "", line)
            message = re.findall(LOG_MESSAGE_PATTERN, line)
            message = " ".join([str(x) for x in message])
            message = re.sub(TIME_STAMP_PATTERN, "", message).strip()

            log = {}
            log["timestamp"] = timestamp
            log["level"] = level
            log["message"] = message
            logs.append(log)
            line = buf.readline()

        return logs
