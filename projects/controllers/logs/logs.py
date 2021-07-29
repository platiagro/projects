# -*- coding: utf-8 -*-
"""Logs controller."""
import datetime
import io
import re
import dateutil.parser
from typing import List, Optional

from projects.kfp.runs import get_latest_run_id
from projects.kubernetes.argo import list_workflow_pods
from projects.kubernetes.seldon import list_deployment_pods
from projects.kubernetes.utils import get_container_logs
from projects.schemas.log import Log, LogList

EXCLUDE_CONTAINERS = ["istio-proxy", "wait"]
LOG_PATTERN = re.compile(r"(.*?)\s(INFO|WARN|WARNING|ERROR|DEBUG)\s*(.*)")
LOG_LEVELS = {
    'info': 'INFO',
    'debug': 'DEBUG',
    'error': 'ERROR',
    'warn': 'ERROR',
}


class LogController:

    def list_logs(self, project_id: str, run_id: str, experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
        """
        Lists logs from a run.

        Parameters
        ----------
        project_id : str
        run_id : str
            The run_id. If `run_id=latest`, then returns logs from the latest run_id.
        experiment_id : str or None
        deployment_id : str or None

        Returns
        -------
        dict
            A dict of logs from a run.
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id or deployment_id)

        pods = []

        if deployment_id is not None:
            # Tries to retrieve any pods associated to a seldondeployment
            pods.extend(
                list_deployment_pods(deployment_id=deployment_id),
            )

        if len(pods) == 0:
            # BUG: workflows and pods are deleted after 1 day due to a
            # "Garbage Collector" feature of Argo workflows/Kubeflow Pipelines.
            # The link below provide useful information on how to configure log
            # persistence and where to set the Time-to-live (TTL) for workflows:
            # https://github.com/kubeflow/pipelines/issues/844#issuecomment-559841627
            # We can make use of these configurations and fix this bug later.
            pods.extend(
                list_workflow_pods(run_id=run_id),
            )

        # Retrieves logs from all containers in all pods (that were not deleted)
        logs = self.pods_to_logs(pods)

        # for now, we don't want log level as 'WARN' so we will change to 'DEBUG'
        for log in logs:
            log.level = LOG_LEVELS.get(log.level.lower(), 'INFO')

        # Sorts logs by creation date DESC
        logs = sorted(logs, key=lambda l: l.created_at, reverse=True)

        return LogList(
            logs=logs,
            total=len(logs),
        )

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
            Detailed logs with level, title, date and message from a container.
        """
        logs = []
        for pod in pods:
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS:
                    raw_logs = get_container_logs(pod, container)

                    if container.env is None:
                        task_name = pod.metadata.name
                    else:
                        task_name = next((e.value for e in container.env if e.name == "TASK_NAME"), pod.metadata.name)

                    created_at = pod.metadata.creation_timestamp

                    logs.extend(
                        self.split_messages(raw_logs, task_name, created_at),
                    )

        return logs

    def split_messages(self, raw_logs: str, task_name: str, created_at: datetime.datetime):
        """
        Splits raw log text into a list of log schemas.

        Parameters
        ----------
        raw_logs : str
        task_name : str
        created_at : datetime.datetime

        Returns
        -------
        list
            Detailed logs with level, Time Stamp and message from pod container.
        """
        # default return for empty logs
        if raw_logs is None:
            return [
                Log(
                    level="INFO",
                    title=task_name,
                    message="Container is creating...",
                    created_at=created_at,
                ),
            ]

        logs = []
        buffer = io.StringIO(raw_logs)

        message_lines = []
        level = "INFO"

        line = buffer.readline()
        while line:
            line = line.strip("\n")
            # Captures the beginning of a log message (until 1st space char)
            # and tries to parse a datetime and a level from this message.
            match = LOG_PATTERN.match(line)
            if match:
                # Appends the previous lines of log
                if len(message_lines) > 0:
                    logs.append(
                        Log(
                            level=level,
                            title=task_name,
                            message="\n".join(message_lines),
                            created_at=created_at,
                        ),
                    )
                    message_lines = []

                date_str = match.group(1)
                level = match.group(2) or "INFO"
                line = match.group(3)

                message_lines.append(line)
                try:
                    created_at = dateutil.parser.isoparse(date_str)
                except (ValueError, OverflowError):
                    pass
            else:
                # This is necessary to remove kubernetes timestamps
                # of the lines in the message body. This regex will
                # look for timestamp at the beginning of line.
                line = re.sub(
                    r"^([0-9]{4}(-[0-9]{2}){2}T[0-9]{2}(:[0-9]{2}){2}.[0-9]+Z\s)",
                    "", line, 2
                )

                message_lines.append(line)

            line = buffer.readline()

        if len(message_lines) > 0:
            logs.append(
                Log(
                    level=level,
                    title=task_name,
                    message="\n".join(message_lines),
                    created_at=created_at,
                ),
            )

        return logs
